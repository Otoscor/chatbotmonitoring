"""앱 리뷰 관련 스키마"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AppReviewResponse(BaseModel):
    """앱 리뷰 응답 모델"""
    id: int
    review_id: str
    app_name: str
    platform: str
    review_text: Optional[str]
    rating: int
    reviewer_name: Optional[str]
    review_date: Optional[datetime]
    crawled_at: datetime

    class Config:
        from_attributes = True


class AppReviewStatsResponse(BaseModel):
    """앱 리뷰 통계 응답 모델"""
    app_name: str
    total_reviews: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, ...}
    platform_distribution: dict  # {google_play: count, app_store: count}
