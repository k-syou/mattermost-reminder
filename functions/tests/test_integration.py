"""
Integration tests for the complete API flow
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from main import app


@pytest.fixture
def client(mock_user):
    """Test client with dependency override"""
    from dependencies import get_current_user
    from main import app
    
    async def override_get_current_user():
        return mock_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    return {
        "uid": "test-user-123",
        "email": "test@example.com"
    }


@patch('routers.messages.get_db')
@patch('routers.webhooks.get_db')
@patch('routers.messages.httpx')
@patch('routers.messages.db')
@patch('routers.webhooks.db')
def test_complete_flow(
    mock_webhook_db,
    mock_msg_db,
    mock_httpx,
    mock_webhooks_get_db,
    mock_messages_get_db,
    client,
    mock_user,
):
    """Test complete flow: create webhook -> create message -> send message"""
    # list_* use get_db(), so return same mocks as db
    mock_webhooks_get_db.return_value = mock_webhook_db
    mock_messages_get_db.return_value = mock_msg_db

    # Mock webhook creation
    webhook_doc = Mock()
    webhook_doc.id = "webhook-123"
    webhook_doc.to_dict.return_value = {
        "id": "webhook-123",
        "userId": "test-user-123",
        "alias": "Test Webhook",
        "url": "https://example.com/webhook",
        "createdAt": "2026-03-05T00:00:00Z",
        "updatedAt": "2026-03-05T00:00:00Z"
    }
    webhook_doc.get.return_value = webhook_doc
    
    webhook_collection = Mock()
    webhook_collection.add.return_value = (None, Mock(id="webhook-123"))
    webhook_collection.document.return_value = webhook_doc
    webhook_collection.where.return_value = webhook_collection
    webhook_collection.order_by.return_value = webhook_collection
    webhook_collection.stream.return_value = [webhook_doc]
    mock_webhook_db.collection.return_value = webhook_collection
    
    # Mock message creation
    message_doc = Mock()
    message_doc.id = "message-123"
    message_doc.to_dict.return_value = {
        "id": "message-123",
        "userId": "test-user-123",
        "content": "Test message",
        "daysOfWeek": [1, 3, 5],
        "sendTime": "09:00",
        "webhookUrl": "https://example.com/webhook",
        "isActive": True,
        "createdAt": "2026-03-05T00:00:00Z",
        "updatedAt": "2026-03-05T00:00:00Z"
    }
    message_doc.get.return_value = message_doc
    
    message_collection = Mock()
    message_collection.add.return_value = (None, Mock(id="message-123"))
    message_collection.document.return_value = message_doc
    message_collection.where.return_value = message_collection
    message_collection.order_by.return_value = message_collection
    message_collection.stream.return_value = [message_doc]
    mock_msg_db.collection.return_value = message_collection
    
    # Mock HTTP response
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_httpx.AsyncClient.return_value.__aenter__.return_value.post.return_value = mock_response
    
    headers = {"Authorization": "Bearer test-token"}
    
    # Step 1: Create webhook
    webhook_response = client.post(
        "/api/webhooks",
        json={
            "alias": "Test Webhook",
            "url": "https://example.com/webhook"
        },
        headers=headers
    )
    assert webhook_response.status_code == 201
    
    # Step 2: List webhooks
    webhooks_response = client.get("/api/webhooks", headers=headers)
    assert webhooks_response.status_code == 200
    assert len(webhooks_response.json()) == 1
    
    # Step 3: Create message
    message_response = client.post(
        "/api/messages",
        json={
            "content": "Test message",
            "daysOfWeek": [1, 3, 5],
            "sendTime": "09:00",
            "webhookUrl": "https://example.com/webhook",
            "isActive": True
        },
        headers=headers
    )
    assert message_response.status_code == 201
    
    # Step 4: List messages
    messages_response = client.get("/api/messages", headers=headers)
    assert messages_response.status_code == 200
    assert len(messages_response.json()) == 1
    
    # Step 5: Send message immediately
    send_response = client.post(
        "/api/messages/message-123/send",
        headers=headers
    )
    assert send_response.status_code == 200
    assert send_response.json()["success"] is True
