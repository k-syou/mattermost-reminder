"""
FastAPI application for Mattermost message scheduler
"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app, firestore
from dotenv import load_dotenv
from firebase_functions import https_fn, scheduler_fn
from datetime import datetime
import httpx
import pytz
import asyncio

_scheduler_logger = logging.getLogger("scheduler")

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

# CORS: credentials=true requires concrete origins (no "*")
_CORS_ORIGINS = [
    "https://mattermost-reminder.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Import routers (dependencies are imported within routers)
# Ensure proper Python path for Firebase Functions
import sys
import os
functions_dir = os.path.dirname(os.path.abspath(__file__))
if functions_dir not in sys.path:
    sys.path.insert(0, functions_dir)

from routers import webhooks, messages
from scheduler import scheduler_router

# Include routers
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(scheduler_router)  # POST /scheduler/send-messages (for Cloud Run + Cloud Scheduler)

# Firebase: on_schedule in main.py also runs send_scheduled_messages every minute (Asia/Seoul).
# If using Cloud Run only, create a Cloud Scheduler job to POST this URL every minute.


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


def _cors_headers(req: https_fn.Request) -> dict:
    origin = req.headers.get("Origin")
    request_headers = req.headers.get("Access-Control-Request-Headers")
    return {
        # If credentials are used, Access-Control-Allow-Origin cannot be "*"
        "Access-Control-Allow-Origin": origin or "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": request_headers or "Authorization,Content-Type",
        "Access-Control-Allow-Credentials": "true",
        "Vary": "Origin",
    }


@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    """
    Firebase HTTP Function that wraps the FastAPI application
    """
    # Handle CORS preflight early
    if req.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=_cors_headers(req))

    # Convert Firebase Request to ASGI scope
    # ASGI requires headers to be lowercase and in bytes
    headers = []
    for key, value in req.headers.items():
        # Convert header name to lowercase (ASGI spec requirement)
        headers.append([key.lower().encode(), str(value).encode()])
    
    # Get request body - Firebase Functions Request uses get_data() method
    request_body = b""
    try:
        if hasattr(req, "get_data"):
            request_body = req.get_data(as_text=False)
        elif hasattr(req, "data"):
            request_body = req.data if isinstance(req.data, bytes) else str(req.data).encode()
    except Exception:
        request_body = b""
    
    scope = {
        "type": "http",
        "method": req.method,
        "path": req.path,
        "query_string": req.query_string.encode() if req.query_string else b"",
        "headers": headers,
        "server": (req.host.split(":")[0] if ":" in req.host else req.host, 443),
        "client": (req.remote_addr, 0) if req.remote_addr else None,
        "scheme": "https",
    }

    # Create ASGI receive function
    body_received = False

    async def receive():
        nonlocal body_received
        if not body_received:
            body_received = True
            return {"type": "http.request", "body": request_body}
        return {"type": "http.request", "body": b""}

    # Create ASGI send function
    response_status = None
    response_headers = []
    response_body_parts = []

    async def send(message):
        nonlocal response_status, response_headers, response_body_parts
        if message["type"] == "http.response.start":
            response_status = message["status"]
            response_headers = message["headers"]
        elif message["type"] == "http.response.body":
            response_body_parts.append(message.get("body", b""))

    # Run ASGI app
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(app(scope, receive, send))
        except Exception as e:
            # Log the error for debugging
            import traceback
            error_trace = traceback.format_exc()
            print(f"ASGI execution error: {str(e)}")
            print(f"Traceback: {error_trace}")
            # If ASGI execution fails, return error response
            return https_fn.Response(
                f'{{"error": "Internal server error: {str(e)}", "detail": "{error_trace}"}}',
                status=500,
                headers={**{"Content-Type": "application/json"}, **_cors_headers(req)}
            )
        finally:
            loop.close()
    except Exception as e:
        # Log the error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"ASGI setup error: {str(e)}")
        print(f"Traceback: {error_trace}")
        # If ASGI execution fails, return error response
        return https_fn.Response(
            f'{{"error": "Internal server error: {str(e)}", "detail": "{error_trace}"}}',
            status=500,
            headers={**{"Content-Type": "application/json"}, **_cors_headers(req)}
        )

    # Build response
    status_code = response_status if response_status else 500
    headers = {k.decode(): v.decode() for k, v in response_headers}
    
    # FastAPI CORSMiddleware already adds CORS headers
    # Remove any duplicate CORS headers that might have been added
    # Keep only the first occurrence of each CORS header
    cors_header_names = ["access-control-allow-origin", "access-control-allow-methods", 
                         "access-control-allow-headers", "access-control-allow-credentials", "vary"]
    seen_cors_headers = set()
    filtered_headers = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if key_lower in cors_header_names:
            if key_lower not in seen_cors_headers:
                seen_cors_headers.add(key_lower)
                filtered_headers[key] = value
        else:
            filtered_headers[key] = value
    
    body = b"".join(response_body_parts)
    # On 5xx, ensure CORS is present (app error path may not have it)
    if status_code >= 500 and "access-control-allow-origin" not in {k.lower() for k in filtered_headers}:
        filtered_headers = {**filtered_headers, **_cors_headers(req)}
    return https_fn.Response(
        body.decode("utf-8") if isinstance(body, bytes) else body,
        status=status_code,
        headers=filtered_headers
    )


# Lazy initialization of Firestore client for scheduled function
_scheduled_db = None

def get_scheduled_db():
    """Get Firestore client with lazy initialization for scheduled function"""
    global _scheduled_db
    if _scheduled_db is None:
        _scheduled_db = firestore.client()
    return _scheduled_db


def _write_send_log_sync(db, message_id: str, user_id: str, status: str, sent_at, error: str = None, content_preview: str = None):
    """Persist one send attempt to send_logs (sync, for Firebase scheduled function)."""
    try:
        doc = {
            "messageId": message_id,
            "userId": user_id,
            "status": status,
            "sentAt": sent_at,
            "createdAt": firestore.SERVER_TIMESTAMP,
        }
        if error:
            doc["error"] = str(error)[:500]
        if content_preview is not None:
            doc["contentPreview"] = (content_preview or "")[:200]
        db.collection("send_logs").add(doc)
    except Exception as e:
        _scheduler_logger.warning("Failed to write send_log: %s", e)


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
    db = get_scheduled_db()
    seoul_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul_tz)
    current_day = (now.weekday() + 1) % 7  # 0=Sun, 6=Sat to match API
    current_time = now.strftime("%H:%M")

    _scheduler_logger.info(
        "Scheduler run at %s (day=%s, time=%s)",
        now.isoformat(),
        current_day,
        current_time,
    )

    messages_ref = db.collection("messages")
    query = messages_ref.where("isActive", "==", True)

    messages_to_send = []
    all_active = 0
    for doc in query.stream():
        all_active += 1
        data = doc.to_dict() or {}
        days_of_week = data.get("daysOfWeek", [])
        send_time = data.get("sendTime", "")
        user_id = data.get("userId", "")
        matched = current_day in days_of_week and send_time == current_time
        _scheduler_logger.info(
            "  message %s: daysOfWeek=%s sendTime=%s -> match=%s",
            doc.id,
            days_of_week,
            send_time,
            matched,
        )
        if matched:
            messages_to_send.append({
                "id": doc.id,
                "userId": user_id,
                "content": data.get("content", ""),
                "webhookUrl": data.get("webhookUrl", ""),
            })

    _scheduler_logger.info("Active messages=%s, matched for send=%s", all_active, len(messages_to_send))

    results = []
    for message in messages_to_send:
        content_preview = (message["content"] or "")[:200]
        sent_at = datetime.now(seoul_tz)
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
                "sentAt": sent_at.isoformat(),
            })
            _write_send_log_sync(
                db,
                message["id"],
                message["userId"],
                "success",
                sent_at,
                content_preview=content_preview,
            )
            _scheduler_logger.info("  sent messageId=%s success", message["id"])
        except Exception as e:
            results.append({
                "id": message["id"],
                "status": "error",
                "error": str(e),
                "sentAt": sent_at.isoformat(),
            })
            _write_send_log_sync(
                db,
                message["id"],
                message["userId"],
                "error",
                sent_at,
                error=str(e),
                content_preview=content_preview,
            )
            _scheduler_logger.warning("  send messageId=%s error: %s", message["id"], e)

    _scheduler_logger.info(
        "Scheduler done: processed=%s success=%s errors=%s",
        len(results),
        sum(1 for r in results if r["status"] == "success"),
        sum(1 for r in results if r["status"] == "error"),
    )
