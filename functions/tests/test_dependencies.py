"""
Tests for authentication dependencies
"""
import pytest
from fastapi import HTTPException
from unittest.mock import Mock, patch
from dependencies import get_current_user


@pytest.mark.asyncio
async def test_get_current_user_success(mock_user, mock_auth_token):
    """Test successful user authentication"""
    from dependencies import auth as auth_module
    with patch.object(auth_module, 'verify_id_token', return_value=mock_user):
        result = await get_current_user(f"Bearer {mock_auth_token}")
        
        assert result["uid"] == mock_user["uid"]
        assert result["email"] == mock_user["email"]


@pytest.mark.asyncio
async def test_get_current_user_no_header():
    """Test authentication without header"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(None)
    
    assert exc_info.value.status_code == 401
    assert "required" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_invalid_header():
    """Test authentication with invalid header format"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("InvalidToken")
    
    assert exc_info.value.status_code == 401
    assert "bearer" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_auth_token):
    """Test authentication with invalid token"""
    from dependencies import auth as auth_module
    from firebase_admin import auth
    with patch.object(auth_module, 'verify_id_token', side_effect=auth.InvalidIdTokenError("Invalid token")):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(f"Bearer {mock_auth_token}")
        
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_expired_token(mock_auth_token):
    """Test authentication with expired token"""
    from dependencies import auth as auth_module
    from firebase_admin import auth
    
    # Create a mock exception that will be caught as ExpiredIdTokenError
    # Note: ExpiredIdTokenError may be a subclass of InvalidIdTokenError
    # So we'll test that the exception is properly handled
    try:
        # Try to create ExpiredIdTokenError - if it fails, use InvalidIdTokenError
        expired_error = auth.ExpiredIdTokenError("Expired token", cause=None)
    except TypeError:
        # If ExpiredIdTokenError constructor is different, use Exception
        expired_error = Exception("Token expired")
    
    with patch.object(auth_module, 'verify_id_token', side_effect=expired_error):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(f"Bearer {mock_auth_token}")
        
        assert exc_info.value.status_code == 401
        # The error should be caught and return 401
        assert "authentication" in exc_info.value.detail.lower() or "expired" in exc_info.value.detail.lower()
