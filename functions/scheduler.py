"""
Firebase Cloud Scheduler function for sending scheduled messages
This will be deployed as a scheduled function that runs every minute

Note: For Python Firebase Functions, we'll use Cloud Scheduler with HTTP trigger
or implement as a separate FastAPI endpoint that can be called by Cloud Scheduler
"""
import logging
from datetime import datetime
from firebase_admin import firestore, initialize_app
from fastapi import APIRouter, HTTPException
import httpx
import pytz

logger = logging.getLogger(__name__)

# Initialize Firebase if not already initialized
try:
    initialize_app()
except ValueError:
    pass  # Already initialized

# Lazy initialization of Firestore client
_db = None

def get_db():
    """Get Firestore client with lazy initialization"""
    global _db
    if _db is None:
        _db = firestore.client()
    return _db

# For backward compatibility with tests
class LazyDB:
    """Lazy wrapper for Firestore client"""
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = LazyDB()

# Create router for scheduler endpoint
scheduler_router = APIRouter()


def _write_send_log(db, message_id: str, user_id: str, status: str, sent_at, error: str = None, content_preview: str = None):
    """Persist one send attempt to send_logs for history."""
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
        logger.warning("Failed to write send_log: %s", e)


@scheduler_router.post("/scheduler/send-messages")
async def send_scheduled_messages():
    """
    Check for messages that should be sent now and send them to Mattermost
    This endpoint should be called by Cloud Scheduler every minute
    """
    db = get_db()
    seoul_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul_tz)
    current_day = (now.weekday() + 1) % 7  # 0=Sun, 6=Sat to match API
    current_time = now.strftime("%H:%M")

    logger.info(
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
        logger.info(
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

    logger.info("Active messages=%s, matched for send=%s", all_active, len(messages_to_send))

    results = []
    for message in messages_to_send:
        content_preview = (message["content"] or "")[:200]
        sent_at = datetime.now(seoul_tz)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
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
            _write_send_log(
                db,
                message["id"],
                message["userId"],
                "success",
                sent_at,
                content_preview=content_preview,
            )
            logger.info("  sent messageId=%s success", message["id"])
        except Exception as e:
            results.append({
                "id": message["id"],
                "status": "error",
                "error": str(e),
                "sentAt": sent_at.isoformat(),
            })
            _write_send_log(
                db,
                message["id"],
                message["userId"],
                "error",
                sent_at,
                error=str(e),
                content_preview=content_preview,
            )
            logger.warning("  send messageId=%s error: %s", message["id"], e)

    summary = {
        "processed": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "results": results,
        "checkedAt": now.isoformat(),
    }
    logger.info(
        "Scheduler done: processed=%s success=%s errors=%s",
        summary["processed"],
        summary["success"],
        summary["errors"],
    )
    return summary
