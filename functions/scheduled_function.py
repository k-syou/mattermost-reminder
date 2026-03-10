"""
Firebase Scheduled Function for sending scheduled messages
This function runs every minute via Cloud Scheduler
"""
import logging
from firebase_functions import scheduler_fn
from firebase_admin import initialize_app, firestore
from datetime import datetime
import httpx
import pytz
from template_utils import render_message_template
from message_utils import get_send_times_from_range

logger = logging.getLogger(__name__)

# Initialize Firebase Admin (if not already initialized)
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


def _write_send_log(db, message_id: str, user_id: str, status: str, sent_at, error: str = None, content_preview: str = None):
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
    db = get_db()
    seoul_tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(seoul_tz)
    current_day = (now.weekday() + 1) % 7
    current_time = now.strftime("%H:%M")

    logger.info("Scheduler run at %s (day=%s, time=%s)", now.isoformat(), current_day, current_time)

    messages_ref = db.collection("messages")
    query = messages_ref.where("isActive", "==", True)
    messages_to_send = []
    all_active = 0
    for doc in query.stream():
        all_active += 1
        data = doc.to_dict() or {}
        days_of_week = data.get("daysOfWeek", [])
        tr_start = data.get("timeRangeStart")
        tr_end = data.get("timeRangeEnd")
        interval_min = data.get("intervalMinutes")
        if tr_start and tr_end and interval_min is not None:
            send_times = get_send_times_from_range(tr_start, tr_end, int(interval_min))
        else:
            send_times = data.get("sendTimes")
            if not send_times or not isinstance(send_times, list):
                send_times = [data.get("sendTime", "")]
            send_times = [t for t in send_times if isinstance(t, str) and len(t) == 5]
        repeat_cycle = data.get("repeatCycle", "weekly")
        day_ok = (repeat_cycle == "daily") or (current_day in days_of_week)
        time_ok = current_time in send_times
        matched = day_ok and time_ok
        logger.info("  message %s: daysOfWeek=%s sendTimes=%s repeatCycle=%s -> match=%s", doc.id, days_of_week, send_times, repeat_cycle, matched)
        if matched:
            messages_to_send.append({
                "id": doc.id,
                "userId": data.get("userId", ""),
                "content": data.get("content", ""),
                "webhookUrl": data.get("webhookUrl", ""),
                "sendOnce": data.get("sendOnce", False),
            })

    logger.info("Active messages=%s, matched for send=%s", all_active, len(messages_to_send))

    results = []
    for message in messages_to_send:
        sent_at = datetime.now(seoul_tz)
        rendered_content = render_message_template(message["content"] or "", sent_at)
        content_preview = (rendered_content or "")[:200]
        try:
            response = httpx.post(
                message["webhookUrl"],
                json={"text": rendered_content},
                timeout=10.0
            )
            response.raise_for_status()
            results.append({"id": message["id"], "status": "success", "sentAt": sent_at.isoformat()})
            _write_send_log(db, message["id"], message["userId"], "success", sent_at, content_preview=content_preview)
            if message.get("sendOnce"):
                db.collection("messages").document(message["id"]).update({
                    "isActive": False,
                    "updatedAt": firestore.SERVER_TIMESTAMP,
                })
            logger.info("  sent messageId=%s success", message["id"])
        except Exception as e:
            results.append({"id": message["id"], "status": "error", "error": str(e), "sentAt": sent_at.isoformat()})
            _write_send_log(db, message["id"], message["userId"], "error", sent_at, error=str(e), content_preview=content_preview)
            logger.warning("  send messageId=%s error: %s", message["id"], e)

    logger.info("Scheduler done: processed=%s success=%s errors=%s", len(results), sum(1 for r in results if r["status"] == "success"), sum(1 for r in results if r["status"] == "error"))
