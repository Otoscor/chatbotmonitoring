"""
크롤러 공통 데이터 모델

모든 크롤러에서 사용하는 공통 데이터 구조를 정의합니다.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class CharacterData:
    """캐릭터 데이터 모델

    캐릭터 챗봇 서비스에서 수집하는 캐릭터 정보를 담는 공통 데이터 구조입니다.
    """
    character_id: str
    rank: int
    name: str
    author: Optional[str] = None
    views: int = 0
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    character_url: Optional[str] = None

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'character_id': self.character_id,
            'rank': self.rank,
            'name': self.name,
            'author': self.author,
            'views': self.views,
            'tags': self.tags,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'character_url': self.character_url,
        }


@dataclass
class CrawledPost:
    """크롤링된 게시글 데이터 모델

    커뮤니티에서 수집하는 게시글 정보를 담는 공통 데이터 구조입니다.
    """
    post_id: str
    gallery_id: str
    title: str
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    view_count: int = 0
    recommend_count: int = 0
    comment_count: int = 0
    url: Optional[str] = None
    content: Optional[str] = None

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'post_id': self.post_id,
            'gallery_id': self.gallery_id,
            'title': self.title,
            'author': self.author,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'view_count': self.view_count,
            'recommend_count': self.recommend_count,
            'comment_count': self.comment_count,
            'url': self.url,
            'content': self.content,
        }


@dataclass
class NewsArticle:
    """뉴스 기사 데이터 모델"""
    article_id: str
    source: str
    title: str
    description: Optional[str] = None
    url: str = ""
    publisher: Optional[str] = None
    published_at: Optional[datetime] = None
    keyword: Optional[str] = None

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'article_id': self.article_id,
            'source': self.source,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'publisher': self.publisher,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'keyword': self.keyword,
        }


@dataclass
class AppReviewData:
    """앱 리뷰 데이터 모델"""
    review_id: str
    app_name: str
    platform: str
    review_text: Optional[str] = None
    rating: int = 0
    reviewer_name: Optional[str] = None
    review_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'review_id': self.review_id,
            'app_name': self.app_name,
            'platform': self.platform,
            'review_text': self.review_text,
            'rating': self.rating,
            'reviewer_name': self.reviewer_name,
            'review_date': self.review_date.isoformat() if self.review_date else None,
        }
