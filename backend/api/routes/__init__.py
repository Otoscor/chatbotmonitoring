"""
API 라우트 모듈

모든 도메인별 라우터를 통합합니다.
"""
from fastapi import APIRouter

from .posts import router as posts_router
from .reports import router as reports_router
from .keywords import router as keywords_router
from .crawl import router as crawl_router
from .characters import router as characters_router
from .news import router as news_router
from .reviews import router as reviews_router
from .bookmarks import router as bookmarks_router
from .samples import router as samples_router

# 메인 라우터
router = APIRouter()

# 각 도메인 라우터 등록
router.include_router(posts_router, tags=["posts"])
router.include_router(reports_router, tags=["reports"])
router.include_router(keywords_router, tags=["keywords"])
router.include_router(crawl_router, tags=["crawl"])
router.include_router(characters_router, tags=["characters"])
router.include_router(news_router, tags=["news"])
router.include_router(reviews_router, tags=["reviews"])
router.include_router(bookmarks_router, tags=["bookmarks"])
router.include_router(samples_router, tags=["samples"])

__all__ = ['router']
