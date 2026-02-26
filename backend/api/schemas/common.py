"""공통 스키마"""
from typing import Optional
from pydantic import BaseModel


class CrawlRequest(BaseModel):
    """크롤링 요청 모델"""
    gallery_id: Optional[str] = None
    pages: Optional[int] = 5


class CrawlResponse(BaseModel):
    """크롤링 응답 모델"""
    success: bool
    message: str
    posts_count: int
