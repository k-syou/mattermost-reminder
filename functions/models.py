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


_TIME_PATTERN = r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$'


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    daysOfWeek: List[int] = Field(..., min_length=1, max_length=7)
    sendTime: str = Field(..., pattern=_TIME_PATTERN)
    sendTimes: Optional[List[str]] = None
    repeatCycle: Optional[str] = Field(default="weekly", pattern=r'^(daily|weekly)$')
    sendOnce: bool = False
    timeRangeStart: Optional[str] = Field(None, pattern=_TIME_PATTERN)  # N분 간격 반복 시작
    timeRangeEnd: Optional[str] = Field(None, pattern=_TIME_PATTERN)    # N분 간격 반복 종료
    intervalMinutes: Optional[int] = Field(None, ge=5, le=60)          # 5,10,15,30,60
    webhookUrl: HttpUrl
    isActive: bool = True


class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    daysOfWeek: Optional[List[int]] = Field(None, min_length=1, max_length=7)
    sendTime: Optional[str] = Field(None, pattern=_TIME_PATTERN)
    sendTimes: Optional[List[str]] = Field(None, min_length=1, max_length=24)
    repeatCycle: Optional[str] = Field(None, pattern=r'^(daily|weekly)$')
    sendOnce: Optional[bool] = None
    timeRangeStart: Optional[str] = Field(None, pattern=_TIME_PATTERN)
    timeRangeEnd: Optional[str] = Field(None, pattern=_TIME_PATTERN)
    intervalMinutes: Optional[int] = Field(None, ge=5, le=60)
    webhookUrl: Optional[HttpUrl] = None
    isActive: Optional[bool] = None


class MessageResponse(BaseModel):
    id: str
    userId: str
    content: str
    daysOfWeek: List[int]
    sendTime: str
    sendTimes: List[str] = []
    repeatCycle: str = "weekly"
    sendOnce: bool = False
    timeRangeStart: Optional[str] = None
    timeRangeEnd: Optional[str] = None
    intervalMinutes: Optional[int] = None
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


class MessageAIGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)


class MessageAIGenerateResponse(BaseModel):
    content: str
    daysOfWeek: Optional[List[int]] = None  # 0=Sun .. 6=Sat
    sendTime: Optional[str] = None  # HH:MM
