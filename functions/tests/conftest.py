"""
Pytest configuration and fixtures
"""
import sys
import os

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch
from firebase_admin import auth


@pytest.fixture
def mock_user():
    """Mock Firebase Auth user"""
    return {
        "uid": "test-user-123",
        "email": "test@example.com",
        "name": "Test User"
    }


@pytest.fixture
def mock_auth_token():
    """Mock Firebase Auth token"""
    return "mock-firebase-token-12345"


@pytest.fixture
def mock_firestore_doc():
    """Mock Firestore document"""
    def _create_doc(data, doc_id="test-doc-id"):
        doc = Mock()
        doc.id = doc_id
        doc.to_dict.return_value = data
        doc.exists = True
        return doc
    return _create_doc


@pytest.fixture
def mock_firestore_collection():
    """Mock Firestore collection"""
    collection = Mock()
    collection.stream.return_value = []
    collection.where.return_value = collection
    collection.order_by.return_value = collection
    collection.document.return_value = Mock()
    collection.add.return_value = (None, Mock(id="new-doc-id"))
    return collection


@pytest.fixture(autouse=True)
def mock_firestore_client():
    """Auto-mock Firestore client for all tests to prevent DefaultCredentialsError"""
    mock_db = Mock()
    mock_collection = Mock()
    mock_collection.stream.return_value = []
    mock_collection.where.return_value = mock_collection
    mock_collection.order_by.return_value = mock_collection
    mock_collection.document.return_value = Mock()
    mock_collection.add.return_value = (None, Mock(id="new-doc-id"))
    mock_db.collection.return_value = mock_collection
    
    # Mock get_db functions and firestore.client to prevent DefaultCredentialsError
    with patch('routers.webhooks.get_db', return_value=mock_db), \
         patch('routers.messages.get_db', return_value=mock_db), \
         patch('scheduler.get_db', return_value=mock_db), \
         patch('main.get_db', return_value=mock_db), \
         patch('firebase_admin.firestore.client', return_value=mock_db):
        yield mock_db
