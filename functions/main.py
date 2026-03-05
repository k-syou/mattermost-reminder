"""
FastAPI application for Mattermost message scheduler
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app, firestore
from dotenv import load_dotenv
from firebase_functions import https_fn, scheduler_fn
from mangum import Mangum
from datetime import datetime
import asyncio
import httpx
import pytz

load_dotenv()

# Initialize Firebase Admin
# Note: For Firebase Functions, initialization should happen in http_function.py
# This is for local development only
try:
    from firebase_admin import get_app
    get_app()
except ValueError:
    # App doesn't exist, initialize it
    # Use Application Default Credentials in production
    # For local development, use service account key
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        initialize_app(cred)
    else:
        # Try to initialize with default credentials
        # This will fail in Firebase Functions deployment if not already initialized
        try:
            initialize_app()
        except Exception:
            # If initialization fails, db will be None and will be initialized later
            pass

# Lazy initialization of Firestore client
_db = None

def get_db():
    """Get Firestore client with lazy initialization"""
    global _db
    if _db is None:
        # Ensure Firebase Admin is initialized
        try:
            from firebase_admin import get_app
            get_app()
        except ValueError:
            # Try to initialize
            if os.path.exists('serviceAccountKey.json'):
                cred = credentials.Certificate('serviceAccountKey.json')
                initialize_app(cred)
            else:
                initialize_app()
        _db = firestore.client()
    return _db

# For backward compatibility, create db variable that uses lazy initialization
class LazyDB:
    """Lazy wrapper for Firestore client"""
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = LazyDB()

app = FastAPI(
    title="Mattermost Scheduler API",
    description="API for scheduling recurring messages to Mattermost via webhooks",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers (dependencies are imported within routers)
# Ensure proper Python path for Firebase Functions
import sys
import os
functions_dir = os.path.dirname(os.path.abspath(__file__))
if functions_dir not in sys.path:
    sys.path.insert(0, functions_dir)

from routers import webhooks, messages

# Include routers
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])

# Note: Scheduler endpoint is available at /scheduler/send-messages
# but for Firebase Functions, we use scheduled_function.py instead


@app.get("/")
async def root():
    return {
        "message": "Mattermost Scheduler API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Firebase Functions - must be defined in main.py for discovery
from mangum import Mangum

# Create ASGI adapter for FastAPI
handler = Mangum(app, lifespan="off")


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
_scheduled_db = None

def get_scheduled_db():
    """Get Firestore client with lazy initialization for scheduled function"""
    global _scheduled_db
    if _scheduled_db is None:
        _scheduled_db = firestore.client()
    return _scheduled_db


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
    db = get_scheduled_db()
    
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
