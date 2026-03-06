"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class WebhookCreate(BaseModel):
    alias: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl


class WebhookUpdate(BaseModel):
    alias: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[HttpUrl] = None


class WebhookResponse(BaseModel):
    id: str
    userId: str
    alias: str
    url: str
    createdAt: datetime
    updatedAt: datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    daysOfWeek: List[int] = Field(..., min_items=1, max_items=7)
    sendTime: str = Field(..., pattern=r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$')
    webhookUrl: HttpUrl
    isActive: bool = True


class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    daysOfWeek: Optional[List[int]] = Field(None, min_items=1, max_items=7)
    sendTime: Optional[str] = Field(None, pattern=r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$')
    webhookUrl: Optional[HttpUrl] = None
    isActive: Optional[bool] = None


class MessageResponse(BaseModel):
    id: str
    userId: str
    content: str
    daysOfWeek: List[int]
    sendTime: str
    webhookUrl: str
    isActive: bool
    createdAt: datetime
    updatedAt: datetime


class SendLogResponse(BaseModel):
    id: str
    messageId: str
    status: str  # success | error
    sentAt: datetime
    error: Optional[str] = None
    contentPreview: Optional[str] = None
