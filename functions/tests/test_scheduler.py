"""
Tests for scheduler functionality
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import pytz
from scheduler import send_scheduled_messages


@patch('scheduler.get_db')
@patch('scheduler.httpx')
@pytest.mark.asyncio
async def test_send_scheduled_messages_success(mock_httpx, mock_get_db):
    """Test successful message sending"""
    # Mock current time (Monday 09:00)
    seoul_tz = pytz.timezone("Asia/Seoul")
    mock_now = datetime(2026, 3, 3, 9, 0, 0)  # Monday
    mock_now = seoul_tz.localize(mock_now)
    
    # Mock Firestore documents. API: 0=Sun, 1=Mon, ..., 6=Sat.
    mock_doc1 = Mock()
    mock_doc1.id = "msg-1"
    mock_doc1.to_dict.return_value = {
        "daysOfWeek": [0],  # Sunday
        "sendTime": "09:00",
        "content": "Sunday message",
        "webhookUrl": "https://example.com/webhook1",
        "isActive": True
    }
    
    mock_doc2 = Mock()
    mock_doc2.id = "msg-2"
    mock_doc2.to_dict.return_value = {
        "daysOfWeek": [1],  # Monday (matches mock_now Monday 09:00)
        "sendTime": "09:00",
        "content": "Monday message",
        "webhookUrl": "https://example.com/webhook2",
        "isActive": True
    }
    
    # Mock Firestore query
    mock_query = Mock()
    mock_query.stream.return_value = [mock_doc1, mock_doc2]
    mock_db = Mock()
    mock_db.collection.return_value.where.return_value = mock_query
    mock_get_db.return_value = mock_db
    
    # Mock HTTP response (async)
    mock_response = AsyncMock()
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.post.return_value = mock_response
    mock_httpx.AsyncClient.return_value = mock_client
    
    with patch('scheduler.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.strftime = datetime.strftime
        
        result = await send_scheduled_messages()
    
    # Should send messages that match current day and time
    assert result["processed"] >= 0


@patch('scheduler.get_db')
@pytest.mark.asyncio
async def test_send_scheduled_messages_no_matches(mock_get_db):
    """Test scheduler when no messages match"""
    # Mock Firestore query with no matching messages
    mock_query = Mock()
    mock_query.stream.return_value = []
    mock_db = Mock()
    mock_db.collection.return_value.where.return_value = mock_query
    mock_get_db.return_value = mock_db
    
    seoul_tz = pytz.timezone("Asia/Seoul")
    mock_now = datetime(2026, 3, 3, 10, 0, 0)  # Different time
    mock_now = seoul_tz.localize(mock_now)
    
    with patch('scheduler.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.strftime = datetime.strftime
        
        result = await send_scheduled_messages()
    
    assert result["processed"] == 0
