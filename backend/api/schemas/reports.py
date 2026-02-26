"""리포트 관련 스키마"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class KeywordResponse(BaseModel):
    """키워드 응답 모델"""
    keyword: str
    count: int
    score: float


class CharacterRankingResponse(BaseModel):
    """캐릭터 랭킹 응답 모델"""
    name: str
    mentions: int
    rank: int


class DailyReportResponse(BaseModel):
    """일일 리포트 응답 모델"""
    id: int
    report_date: datetime
    total_posts: int
    total_views: int
    total_recommends: int
    total_comments: int
    top_keywords: Optional[List[dict]]
    top_characters: Optional[List[dict]]
    trending_topics: Optional[List[dict]]

    class Config:
        from_attributes = True
