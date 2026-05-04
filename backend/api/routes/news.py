"""
뉴스 API 라우트
"""
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, NewsArticle
from api.schemas.news import NewsArticleResponse, CrawlNewsRequest
from crawler.news_crawler import crawl_all_news

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/news", response_model=List[NewsArticleResponse])
async def get_news(
    source: Optional[str] = Query(None, description="소스 필터 (naver, google)"),
    keyword: Optional[str] = Query(None, description="키워드 필터"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    뉴스 기사 목록 조회
    최신 기사순으로 정렬
    """
    query = select(NewsArticle).order_by(desc(NewsArticle.published_at))

    if source:
        query = query.where(NewsArticle.source == source)
    if keyword:
        query = query.where(NewsArticle.keyword == keyword)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    articles = result.scalars().all()

    return articles


@router.get("/news/latest", response_model=List[NewsArticleResponse])
async def get_latest_news(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    최신 뉴스 기사 조회 (24시간 이내)
    """
    since = datetime.now() - timedelta(hours=24)

    query = select(NewsArticle).where(
        NewsArticle.crawled_at >= since
    ).order_by(desc(NewsArticle.published_at)).limit(limit)

    result = await db.execute(query)
    articles = result.scalars().all()

    return articles


@router.get("/news/sources")
async def get_news_sources(db: AsyncSession = Depends(get_db)):
    """
    뉴스 소스별 기사 수 조회
    """
    query = select(
        NewsArticle.source,
        func.count(NewsArticle.id).label("count")
    ).group_by(NewsArticle.source)

    result = await db.execute(query)
    sources = result.all()

    return [{"source": s.source, "count": s.count} for s in sources]


@router.post("/news/crawl")
async def crawl_news_endpoint(
    request: CrawlNewsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    뉴스 크롤링 트리거
    네이버 + 구글 뉴스 수집
    """
    try:
        # 크롤링 실행
        results = await crawl_all_news(
            sources=request.sources,
            keywords=request.keywords,
            limit_per_keyword=20
        )

        # DB에 저장 (중복 제거)
        saved_count = 0
        for source_name, articles in results.items():
            for article_data in articles:
                # 중복 체크
                existing = await db.execute(
                    select(NewsArticle).where(NewsArticle.article_id == article_data.article_id)
                )
                if existing.scalar_one_or_none():
                    continue

                article = NewsArticle(
                    article_id=article_data.article_id,
                    source=article_data.source,
                    title=article_data.title,
                    description=article_data.description,
                    url=article_data.url,
                    publisher=article_data.publisher,
                    published_at=article_data.published_at,
                    keyword=article_data.keyword
                )
                db.add(article)
                saved_count += 1

        await db.commit()

        total_crawled = sum(len(articles) for articles in results.values())

        return {
            "success": True,
            "message": f"뉴스 크롤링 완료: {total_crawled}개 수집, {saved_count}개 저장",
            "results": {
                source: len(articles) for source, articles in results.items()
            }
        }
    except Exception as e:
        logger.error(f"뉴스 크롤링 실패: {e}")
        return {
            "success": False,
            "message": f"크롤링 실패: {str(e)}",
            "results": {}
        }
