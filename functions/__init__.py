# Firebase Functions package
# Export all functions for Firebase Functions deployment

"""
Firebase Functions Python SDK requires functions to be defined or imported
at the module level in __init__.py for discovery during deployment.
"""

from firebase_functions import https_fn, scheduler_fn
from firebase_admin import initialize_app
from mangum import Mangum
from datetime import datetime
import asyncio
import httpx
import pytz
from firebase_admin import firestore

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


# Lazy initialization of Firestore client for scheduled function
_db = None

def get_db():
    """Get Firestore client with lazy initialization"""
    global _db
    if _db is None:
        _db = firestore.client()
    return _db


@scheduler_fn.on_schedule(
    schedule="every 1 minutes",
    timezone="Asia/Seoul",
    region="asia-northeast3"
)
def send_scheduled_messages(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Check for messages that should be sent now and send them to Mattermost
    This function is triggered by Cloud Scheduler every minute
    """
    # Get Firestore client (lazy initialization)
    db = get_db()
    
    # Get current time in Asia/Seoul timezone
    seoul_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul_tz)
    current_day = now.weekday()  # 0=Monday, 6=Sunday
    current_time = now.strftime("%H:%M")
    
    # Query active messages
    messages_ref = db.collection("messages")
    query = messages_ref.where("isActive", "==", True)
    
    messages_to_send = []
    for doc in query.stream():
        data = doc.to_dict()
        days_of_week = data.get("daysOfWeek", [])
        send_time = data.get("sendTime", "")
        
        # Check if current day matches and time matches
        if current_day in days_of_week and send_time == current_time:
            messages_to_send.append({
                "id": doc.id,
                "content": data.get("content", ""),
                "webhookUrl": data.get("webhookUrl", "")
            })
    
    # Send messages
    results = []
    for message in messages_to_send:
        try:
            response = httpx.post(
                message["webhookUrl"],
                json={"text": message["content"]},
                timeout=10.0
            )
            response.raise_for_status()
            results.append({
                "id": message["id"],
                "status": "success",
                "sentAt": datetime.now(seoul_tz).isoformat()
            })
        except Exception as e:
            results.append({
                "id": message["id"],
                "status": "error",
                "error": str(e),
                "sentAt": datetime.now(seoul_tz).isoformat()
            })
    
    print(f"Processed {len(results)} messages: {sum(1 for r in results if r['status'] == 'success')} success, {sum(1 for r in results if r['status'] == 'error')} errors")

__all__ = ['api', 'send_scheduled_messages']
