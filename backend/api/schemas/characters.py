"""캐릭터 서비스 관련 스키마"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ChatServiceCharacterResponse(BaseModel):
    """캐릭터챗 서비스 캐릭터 응답 모델"""
    id: int
    service: str
    character_id: str
    rank: int
    name: str
    author: Optional[str]
    views: int
    tags: Optional[List[str]]
    description: Optional[str]
    thumbnail_url: Optional[str]
    character_url: Optional[str]
    crawled_at: datetime

    class Config:
        from_attributes = True


class CrawlChatServicesRequest(BaseModel):
    """캐릭터챗 서비스 크롤링 요청 모델"""
    services: Optional[List[str]] = None
