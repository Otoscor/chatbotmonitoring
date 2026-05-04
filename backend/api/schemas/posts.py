"""게시글 관련 스키마"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PostResponse(BaseModel):
    """게시글 응답 모델"""
    id: int
    post_id: str
    gallery_id: str
    title: str
    author: Optional[str]
    created_at: Optional[datetime]
    view_count: int
    recommend_count: int
    comment_count: int
    url: Optional[str]

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """통계 응답 모델"""
    total_posts: int
    total_views: int
    total_recommends: int
    total_comments: int
    avg_views: float
    avg_recommends: float
    avg_comments: float
