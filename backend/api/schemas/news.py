"""뉴스 관련 스키마"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class NewsArticleResponse(BaseModel):
    """뉴스 기사 응답 모델"""
    id: int
    article_id: str
    source: str
    title: str
    description: Optional[str]
    url: str
    publisher: Optional[str]
    published_at: Optional[datetime]
    crawled_at: datetime
    keyword: Optional[str]

    class Config:
        from_attributes = True


class CrawlNewsRequest(BaseModel):
    """뉴스 크롤링 요청 모델"""
    sources: Optional[List[str]] = None  # ['naver', 'google']
    keywords: Optional[List[str]] = None  # 사용자 정의 키워드
