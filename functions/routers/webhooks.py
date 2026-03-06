"""
Webhook CRUD API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from typing import List
from datetime import datetime

from dependencies import get_current_user
from models import WebhookCreate, WebhookUpdate, WebhookResponse

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


@router.post("", response_model=WebhookResponse, status_code=201)
async def create_webhook(
    webhook: WebhookCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new webhook"""
    try:
        webhook_data = {
            "userId": current_user["uid"],
            "alias": webhook.alias,
            "url": str(webhook.url),
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection("webhooks").add(webhook_data)
        webhook_id = doc_ref[1].id
        
        # Fetch the created document
        doc = db.collection("webhooks").document(webhook_id).get()
        doc_data = doc.to_dict()
        
        return WebhookResponse(
            id=webhook_id,
            userId=doc_data["userId"],
            alias=doc_data["alias"],
            url=doc_data["url"],
            createdAt=doc_data["createdAt"],
            updatedAt=doc_data["updatedAt"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create webhook: {str(e)}")


@router.get("", response_model=List[WebhookResponse])
async def list_webhooks(current_user: dict = Depends(get_current_user)):
    """Get all webhooks for the current user"""
    try:
        db_client = get_db()
        webhooks_ref = db_client.collection("webhooks")
        query = webhooks_ref.where("userId", "==", current_user["uid"])
        
        # Try to order by createdAt, but fallback if index is missing
        try:
            query = query.order_by("createdAt")
        except Exception:
            # If order_by fails (missing index), continue without ordering
            pass
        
        docs = query.stream()
        webhooks = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            webhooks.append(WebhookResponse(
                id=doc.id,
                userId=doc_data["userId"],
                alias=doc_data["alias"],
                url=doc_data["url"],
                createdAt=doc_data["createdAt"],
                updatedAt=doc_data["updatedAt"]
            ))
        
        # Sort in Python if order_by failed
        if len(webhooks) > 0 and hasattr(webhooks[0], "createdAt"):
            webhooks.sort(key=lambda x: x.createdAt if x.createdAt else 0, reverse=True)
        
        return webhooks
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in list_webhooks: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch webhooks: {str(e)}")


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific webhook by ID"""
    try:
        doc_ref = db.collection("webhooks").document(webhook_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data["userId"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return WebhookResponse(
            id=doc.id,
            userId=doc_data["userId"],
            alias=doc_data["alias"],
            url=doc_data["url"],
            createdAt=doc_data["createdAt"],
            updatedAt=doc_data["updatedAt"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch webhook: {str(e)}")


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    webhook: WebhookUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a webhook"""
    try:
        doc_ref = db.collection("webhooks").document(webhook_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data["userId"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare update data
        update_data = {"updatedAt": firestore.SERVER_TIMESTAMP}
        if webhook.alias is not None:
            update_data["alias"] = webhook.alias
        if webhook.url is not None:
            update_data["url"] = str(webhook.url)
        
        doc_ref.update(update_data)
        
        # Fetch updated document
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        
        return WebhookResponse(
            id=updated_doc.id,
            userId=updated_data["userId"],
            alias=updated_data["alias"],
            url=updated_data["url"],
            createdAt=updated_data["createdAt"],
            updatedAt=updated_data["updatedAt"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update webhook: {str(e)}")


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a webhook"""
    try:
        doc_ref = db.collection("webhooks").document(webhook_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        doc_data = doc.to_dict()
        
        # Check ownership
        if doc_data["userId"] != current_user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        doc_ref.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete webhook: {str(e)}")
