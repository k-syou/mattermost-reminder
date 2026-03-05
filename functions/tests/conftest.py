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
