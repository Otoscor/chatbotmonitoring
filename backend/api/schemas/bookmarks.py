"""북마크 관련 스키마"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    """북마크 생성 요청"""
    url: str
    category: str = 'post'


class BookmarkUpdate(BaseModel):
    """북마크 수정 요청"""
    tags: Optional[List[str]] = None
    user_note: Optional[str] = None
    category: Optional[str] = None


class BookmarkResponse(BaseModel):
    """북마크 응답 모델"""
    id: int
    url: str
    title: Optional[str]
    description: Optional[str]
    ai_summary: Optional[str]
    thumbnail_url: Optional[str]
    site_name: Optional[str]
    category: str
    tags: Optional[List[str]]
    user_note: Optional[str]
    is_summarized: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
