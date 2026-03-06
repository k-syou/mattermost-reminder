"""
Message CRUD API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from typing import List, Any
from datetime import datetime, timezone
import httpx

from dependencies import get_current_user
from models import MessageCreate, MessageUpdate, MessageResponse, SendLogResponse

router = APIRouter()

# Lazy initialization of Firestore client to avoid import-time errors
_db = None

def get_db():
    """Get Firestore client with lazy initialization"""
    global _db
    if _db is None:
        _db = firestore.client()
    return _db

# For backward compatibility
class LazyDB:
    """Lazy wrapper for Firestore client"""
    def __getattr__(self, name):
        # Only call get_db() when attribute is actually accessed
        # This prevents hasattr() checks from triggering firestore.client()
        return getattr(get_db(), name)
    
    def __dir__(self):
        # Provide a list of attributes to help with introspection
        # This prevents hasattr() from calling __getattr__
        try:
            db_instance = get_db()
            return dir(db_instance)
        except Exception:
            # If get_db() fails, return empty list
            return []

db = LazyDB()


def _write_send_log(
    message_id: str,
    user_id: str,
    status: str,
    error: str = None,
    content_preview: str = None,
):
    """Append one send attempt to send_logs collection."""
    try:
        db_client = get_db()
        now = datetime.now(timezone.utc)
        doc = {
            "messageId": message_id,
            "userId": user_id,
            "status": status,
            "sentAt": now,
            "createdAt": firestore.SERVER_TIMESTAMP,
        }
        if error:
            doc["error"] = str(error)[:500]
        if content_preview is not None:
            doc["contentPreview"] = (content_preview or "")[:200]
        db_client.collection("send_logs").add(doc)
    except Exception:
        pass


def _to_datetime(val: Any) -> datetime:
    """Convert Firestore Timestamp to Python datetime for JSON serialization."""
    if val is None:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    if isinstance(val, datetime):
        return val
    if hasattr(val, "timestamp"):
        return datetime.fromtimestamp(val.timestamp(), tz=timezone.utc)
    if hasattr(val, "seconds"):
        secs = val.seconds + getattr(val, "nanoseconds", 0) / 1e9
        return datetime.fromtimestamp(secs, tz=timezone.utc)
    return datetime.fromtimestamp(0, tz=timezone.utc)


@router.post("", response_model=MessageResponse, status_code=201)
async def create_message(
    message: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new scheduled message"""
    try:
        # Validate daysOfWeek (0-6)
        if not all(0 <= day <= 6 for day in message.daysOfWeek):
            raise HTTPException(
                status_code=400,
                detail="daysOfWeek must contain values between 0 (Sunday) and 6 (Saturday)"
            )
        
        message_data = {
            "userId": current_user["uid"],
            "content": message.content,
            "daysOfWeek": message.daysOfWeek,
            "sendTime": message.sendTime,
            "webhookUrl": str(message.webhookUrl),
            "isActive": message.isActive,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection("messages").add(message_data)
        message_id = doc_ref[1].id
        
        # Fetch the created document
        doc = db.collection("messages").document(message_id).get()
        doc_data = doc.to_dict()
        
        return MessageResponse(
            id=message_id,
            userId=doc_data["userId"],
            content=doc_data["content"],
            daysOfWeek=doc_data["daysOfWeek"],
            sendTime=doc_data["sendTime"],
            webhookUrl=doc_data["webhookUrl"],
            isActive=doc_data["isActive"],
            createdAt=_to_datetime(doc_data["createdAt"]),
            updatedAt=_to_datetime(doc_data["updatedAt"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")


@router.get("", response_model=List[MessageResponse])
async def list_messages(current_user: dict = Depends(get_current_user)):
    """Get all messages for the current user"""
    try:
        db_client = get_db()
        query = db_client.collection("messages").where(
            "userId", "==", current_user["uid"]
        )
        docs = query.stream()
        messages = []
        for doc in docs:
            doc_data = doc.to_dict() or {}
            messages.append(
                MessageResponse(
                    id=doc.id,
                    userId=doc_data.get("userId", ""),
                    content=doc_data.get("content", ""),
                    daysOfWeek=doc_data.get("daysOfWeek", []),
                    sendTime=doc_data.get("sendTime", ""),
                    webhookUrl=doc_data.get("webhookUrl", ""),
                    isActive=doc_data.get("isActive", True),
                    createdAt=_to_datetime(doc_data.get("createdAt")),
                    updatedAt=_to_datetime(doc_data.get("updatedAt")),
                )
            )
        messages.sort(
            key=lambda x: x.createdAt.timestamp() if x.createdAt else 0,
            reverse=True,
        )
        return messages
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in list_messages: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


@router.get("/send-logs", response_model=List[SendLogResponse])
async def list_send_logs(
    current_user: dict = Depends(get_current_user),
    limit: int = 100,
):
    """List recent send logs for the current user (success and error)."""
    try:
        db_client = get_db()
        query = (
            db_client.collection("send_logs")
            .where("userId", "==", current_user["uid"])
            .limit(500)
        )
        docs = list(query.stream())
        logs = []
        for doc in docs:
            data = doc.to_dict() or {}
            if data.get("userId") != current_user["uid"]:
                continue
            logs.append(
                SendLogResponse(
                    id=doc.id,
                    messageId=data.get("messageId", ""),
                    status=data.get("status", ""),
                    sentAt=_to_datetime(data.get("sentAt")),
                    error=data.get("error"),
                    contentPreview=data.get("contentPreview"),
                )
            )
        logs.sort(key=lambda x: x.sentAt.timestamp(), reverse=True)
        return logs[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch send logs: {str(e)}"
        )


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific message by ID"""
    try:
        doc_ref = db.collection("messages").document(message_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Message not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data["userId"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return MessageResponse(
            id=doc.id,
            userId=doc_data["userId"],
            content=doc_data["content"],
            daysOfWeek=doc_data["daysOfWeek"],
            sendTime=doc_data["sendTime"],
            webhookUrl=doc_data["webhookUrl"],
            isActive=doc_data["isActive"],
            createdAt=_to_datetime(doc_data["createdAt"]),
            updatedAt=_to_datetime(doc_data["updatedAt"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch message: {str(e)}")


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    message: MessageUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a message"""
    try:
        doc_ref = db.collection("messages").document(message_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Message not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data["userId"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate daysOfWeek if provided
        if message.daysOfWeek is not None:
            if not all(0 <= day <= 6 for day in message.daysOfWeek):
                raise HTTPException(
                    status_code=400,
                    detail="daysOfWeek must contain values between 0 (Sunday) and 6 (Saturday)"
                )
        
        # Prepare update data
        update_data = {"updatedAt": firestore.SERVER_TIMESTAMP}
        if message.content is not None:
            update_data["content"] = message.content
        if message.daysOfWeek is not None:
            update_data["daysOfWeek"] = message.daysOfWeek
        if message.sendTime is not None:
            update_data["sendTime"] = message.sendTime
        if message.webhookUrl is not None:
            update_data["webhookUrl"] = str(message.webhookUrl)
        if message.isActive is not None:
            update_data["isActive"] = message.isActive
        
        doc_ref.update(update_data)
        
        # Fetch updated document
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        
        return MessageResponse(
            id=updated_doc.id,
            userId=updated_data["userId"],
            content=updated_data["content"],
            daysOfWeek=updated_data["daysOfWeek"],
            sendTime=updated_data["sendTime"],
            webhookUrl=updated_data["webhookUrl"],
            isActive=updated_data["isActive"],
            createdAt=_to_datetime(updated_data["createdAt"]),
            updatedAt=_to_datetime(updated_data["updatedAt"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update message: {str(e)}")


@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a message"""
    try:
        doc_ref = db.collection("messages").document(message_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Message not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data["userId"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        doc_ref.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")


@router.post("/{message_id}/send", status_code=200)
async def send_message_now(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Send a message immediately (for testing)"""
    try:
        doc_ref = db.collection("messages").document(message_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Message not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data["userId"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        webhook_url = doc_data["webhookUrl"]
        content = doc_data["content"]
        user_id = doc_data["userId"]
        content_preview = (content or "")[:200]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json={"text": content},
                    timeout=10.0
                )
                response.raise_for_status()
            _write_send_log(message_id, user_id, "success", content_preview=content_preview)
            return {
                "success": True,
                "message": "Message sent successfully",
                "messageId": message_id
            }
        except httpx.HTTPError as e:
            _write_send_log(message_id, user_id, "error", error=str(e), content_preview=content_preview)
            raise HTTPException(
                status_code=502,
                detail=f"Failed to send message to Mattermost: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")
