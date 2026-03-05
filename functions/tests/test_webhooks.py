"""
Tests for webhook API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import Depends
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from main import app
from firebase_admin import firestore


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
def mock_webhook_data():
    return {
        "id": "webhook-123",
        "userId": "test-user-123",
        "alias": "Test Webhook",
        "url": "https://mattermost.example.com/hooks/abc123",
        "createdAt": "2026-03-05T00:00:00Z",
        "updatedAt": "2026-03-05T00:00:00Z"
    }


@patch('routers.webhooks.db')
def test_create_webhook(mock_db, client, mock_webhook_data):
    """Test webhook creation"""
    
    # Mock Firestore
    mock_doc = Mock()
    mock_doc.id = "webhook-123"
    mock_doc.to_dict.return_value = mock_webhook_data
    mock_doc.get.return_value = mock_doc
    
    mock_collection = Mock()
    mock_collection.add.return_value = (None, Mock(id="webhook-123"))
    mock_collection.document.return_value = mock_doc
    mock_db.collection.return_value = mock_collection
    
    response = client.post(
        "/api/webhooks",
        json={
            "alias": "Test Webhook",
            "url": "https://mattermost.example.com/hooks/abc123"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["alias"] == "Test Webhook"
    assert data["url"] == "https://mattermost.example.com/hooks/abc123"


@patch('routers.webhooks.db')
def test_list_webhooks(mock_db, client, mock_webhook_data):
    """Test webhook listing"""
    
    # Mock Firestore query
    mock_doc = Mock()
    mock_doc.id = "webhook-123"
    mock_doc.to_dict.return_value = mock_webhook_data
    
    mock_query = Mock()
    mock_query.stream.return_value = [mock_doc]
    mock_query.where.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    
    mock_db.collection.return_value.where.return_value = mock_query
    
    response = client.get(
        "/api/webhooks",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "webhook-123"


def test_create_webhook_unauthorized():
    """Test webhook creation without authentication"""
    from main import app
    from dependencies import get_current_user
    
    # Don't override dependency - should fail without auth
    test_client = TestClient(app)
    response = test_client.post(
        "/api/webhooks",
        json={"alias": "Test", "url": "https://example.com"}
    )
    
    assert response.status_code == 401
