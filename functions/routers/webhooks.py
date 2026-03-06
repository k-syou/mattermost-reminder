"""
Webhook CRUD API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from typing import List, Any
from datetime import datetime, timezone

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


def _to_datetime(val: Any) -> datetime:
    """Convert Firestore Timestamp to Python datetime for JSON serialization."""
    if val is None:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    if isinstance(val, datetime):
        return val
    if hasattr(val, "timestamp"):
        return datetime.fromtimestamp(val.timestamp(), tz=timezone.utc)
    # google.cloud.firestore_v1.types.Timestamp uses .seconds + .nanoseconds
    if hasattr(val, "seconds"):
        secs = val.seconds + getattr(val, "nanoseconds", 0) / 1e9
        return datetime.fromtimestamp(secs, tz=timezone.utc)
    return datetime.fromtimestamp(0, tz=timezone.utc)


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
            createdAt=_to_datetime(doc_data["createdAt"]),
            updatedAt=_to_datetime(doc_data["updatedAt"]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create webhook: {str(e)}")


@router.get("", response_model=List[WebhookResponse])
async def list_webhooks(current_user: dict = Depends(get_current_user)):
    """Get all webhooks for the current user"""
    try:
        db_client = get_db()
        query = db_client.collection("webhooks").where(
            "userId", "==", current_user["uid"]
        )
        docs = query.stream()
        webhooks = []
        for doc in docs:
            doc_data = doc.to_dict() or {}
            webhooks.append(
                WebhookResponse(
                    id=doc.id,
                    userId=doc_data.get("userId", ""),
                    alias=doc_data.get("alias", ""),
                    url=doc_data.get("url", ""),
                    createdAt=_to_datetime(doc_data.get("createdAt")),
                    updatedAt=_to_datetime(doc_data.get("updatedAt")),
                )
            )
        webhooks.sort(
            key=lambda x: x.createdAt.timestamp() if x.createdAt else 0,
            reverse=True,
        )
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
            createdAt=_to_datetime(doc_data["createdAt"]),
            updatedAt=_to_datetime(doc_data["updatedAt"]),
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
            createdAt=_to_datetime(updated_data["createdAt"]),
            updatedAt=_to_datetime(updated_data["updatedAt"]),
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
