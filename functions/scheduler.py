"""
Firebase Cloud Scheduler function for sending scheduled messages
This will be deployed as a scheduled function that runs every minute

Note: For Python Firebase Functions, we'll use Cloud Scheduler with HTTP trigger
or implement as a separate FastAPI endpoint that can be called by Cloud Scheduler
"""
import os
from datetime import datetime
from firebase_admin import firestore, initialize_app
from fastapi import APIRouter, HTTPException
import httpx
import pytz

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


@scheduler_router.post("/scheduler/send-messages")
async def send_scheduled_messages():
    """
    Check for messages that should be sent now and send them to Mattermost
    This endpoint should be called by Cloud Scheduler every minute
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
                "sentAt": datetime.now(seoul_tz).isoformat()
            })
        except Exception as e:
            results.append({
                "id": message["id"],
                "status": "error",
                "error": str(e),
                "sentAt": datetime.now(seoul_tz).isoformat()
            })
    
    return {
        "processed": len(results),
        "success": sum(1 for r in results if r["status"] == "success"),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "results": results,
        "checkedAt": datetime.now(seoul_tz).isoformat()
    }
