"""
Firebase Functions HTTP wrapper for FastAPI application
"""
from firebase_functions import https_fn
from firebase_admin import initialize_app
from mangum import Mangum
import asyncio

# Initialize Firebase Admin FIRST before importing main
# This ensures credentials are available when main.py is imported
try:
    initialize_app()
except ValueError:
    pass  # Already initialized

# Import main after Firebase Admin is initialized
import main

# Create ASGI adapter for FastAPI
handler = Mangum(main.app, lifespan="off")


@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    """
    Firebase HTTP Function that wraps the FastAPI application
    """
    # Convert Firebase Request to ASGI format
    scope = {
        "type": "http",
        "method": req.method,
        "path": req.path,
        "query_string": req.query_string.encode() if req.query_string else b"",
        "headers": [[k.encode(), v.encode()] for k, v in req.headers.items()],
        "server": (req.host, 443),
        "client": (req.remote_addr, 0),
        "scheme": "https",
    }
    
    # Create a simple receive function
    async def receive():
        return {
            "type": "http.request",
            "body": req.get_data() if hasattr(req, 'get_data') else b"",
        }
    
    # Run the ASGI handler
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(handler(scope, receive, None))
        status_code = response["status"]
        headers = {k.decode(): v.decode() for k, v in response["headers"]}
        body = b"".join(response.get("body", []))
        
        return https_fn.Response(
            body.decode("utf-8") if isinstance(body, bytes) else body,
            status=status_code,
            headers=headers
        )
    finally:
        loop.close()
