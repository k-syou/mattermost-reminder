"""
Tests for message API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from main import app


@pytest.fixture
def client(mock_user_dict):
    """Test client with dependency override"""
    from dependencies import get_current_user
    from main import app
    
    async def override_get_current_user():
        return mock_user_dict
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_dict():
    """Mock user dictionary"""
    return {
        "uid": "test-user-123",
        "email": "test@example.com"
    }


@pytest.fixture
def mock_message_data():
    return {
        "id": "message-123",
        "userId": "test-user-123",
        "content": "Test message",
        "daysOfWeek": [1, 3, 5],
        "sendTime": "09:00",
        "webhookUrl": "https://mattermost.example.com/hooks/abc123",
        "isActive": True,
        "createdAt": "2026-03-05T00:00:00Z",
        "updatedAt": "2026-03-05T00:00:00Z"
    }


@patch('routers.messages.db')
def test_create_message(mock_db, client, mock_message_data):
    """Test message creation"""
    
    # Mock Firestore
    mock_doc = Mock()
    mock_doc.id = "message-123"
    mock_doc.to_dict.return_value = mock_message_data
    mock_doc.get.return_value = mock_doc
    
    mock_collection = Mock()
    mock_collection.add.return_value = (None, Mock(id="message-123"))
    mock_collection.document.return_value = mock_doc
    mock_db.collection.return_value = mock_collection
    
    response = client.post(
        "/api/messages",
        json={
            "content": "Test message",
            "daysOfWeek": [1, 3, 5],
            "sendTime": "09:00",
            "webhookUrl": "https://mattermost.example.com/hooks/abc123",
            "isActive": True
        },
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Test message"
    assert data["daysOfWeek"] == [1, 3, 5]
    assert data["sendTime"] == "09:00"


@patch('routers.messages.db')
def test_create_message_invalid_days(mock_db, client):
    """Test message creation with invalid days"""
    
    response = client.post(
        "/api/messages",
        json={
            "content": "Test",
            "daysOfWeek": [7, 8],  # Invalid days
            "sendTime": "09:00",
            "webhookUrl": "https://example.com"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 400


@patch('routers.messages.httpx')
@patch('routers.messages.db')
def test_send_message_now(mock_db, mock_httpx, client, mock_message_data):
    """Test immediate message sending"""
    
    # Mock Firestore
    mock_doc = Mock()
    mock_doc.id = "message-123"
    mock_doc.to_dict.return_value = mock_message_data
    mock_doc.get.return_value = mock_doc
    
    mock_db.collection.return_value.document.return_value = mock_doc
    
    # Mock HTTP request (async)
    from unittest.mock import AsyncMock
    mock_response = AsyncMock()
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.post.return_value = mock_response
    mock_httpx.AsyncClient.return_value = mock_client
    
    response = client.post(
        "/api/messages/message-123/send",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
