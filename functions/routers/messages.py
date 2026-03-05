"""
Message CRUD API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from typing import List
import httpx

from dependencies import get_current_user
from models import MessageCreate, MessageUpdate, MessageResponse

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
        return getattr(get_db(), name)

db = LazyDB()


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
            createdAt=doc_data["createdAt"],
            updatedAt=doc_data["updatedAt"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")


@router.get("", response_model=List[MessageResponse])
async def list_messages(current_user: dict = Depends(get_current_user)):
    """Get all messages for the current user"""
    try:
        messages_ref = db.collection("messages")
        query = messages_ref.where("userId", "==", current_user["uid"]).order_by("createdAt")
        
        docs = query.stream()
        messages = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            messages.append(MessageResponse(
                id=doc.id,
                userId=doc_data["userId"],
                content=doc_data["content"],
                daysOfWeek=doc_data["daysOfWeek"],
                sendTime=doc_data["sendTime"],
                webhookUrl=doc_data["webhookUrl"],
                isActive=doc_data["isActive"],
                createdAt=doc_data["createdAt"],
                updatedAt=doc_data["updatedAt"]
            ))
        
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


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
            createdAt=doc_data["createdAt"],
            updatedAt=doc_data["updatedAt"]
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
            createdAt=updated_data["createdAt"],
            updatedAt=updated_data["updatedAt"]
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
        
        # Send to Mattermost webhook
        webhook_url = doc_data["webhookUrl"]
        content = doc_data["content"]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json={"text": content},
                    timeout=10.0
                )
                response.raise_for_status()
            
            return {
                "success": True,
                "message": "Message sent successfully",
                "messageId": message_id
            }
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to send message to Mattermost: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")
