"""
앱 리뷰 API 라우트
"""
from collections import Counter
from typing import List, Optional
import logging
import re

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, AppReview
from api.schemas.reviews import AppReviewResponse, AppReviewStatsResponse
from api.utils.date_utils import get_kst_today_boundaries_utc

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/app-reviews/today", response_model=List[AppReviewResponse])
async def get_today_app_reviews(
    db: AsyncSession = Depends(get_db)
):
    """오늘 크롤링한 리뷰 조회 (KST 기준 — crawled_at 기준)"""
    start_utc, end_utc = get_kst_today_boundaries_utc()

    query = select(AppReview).where(
        AppReview.crawled_at >= start_utc,
        AppReview.crawled_at < end_utc,
    ).order_by(AppReview.app_name, desc(AppReview.rating))

    result = await db.execute(query)
    reviews = result.scalars().all()

    return reviews


@router.get("/app-reviews", response_model=List[AppReviewResponse])
async def get_app_reviews(
    app_name: Optional[str] = Query(None, description="앱 이름 필터"),
    platform: Optional[str] = Query(None, description="플랫폼 필터 (google_play, app_store)"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="최소 평점"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """앱 리뷰 목록 조회"""
    query = select(AppReview).order_by(desc(AppReview.review_date))

    if app_name:
        query = query.where(AppReview.app_name == app_name)
    if platform:
        query = query.where(AppReview.platform == platform)
    if min_rating:
        query = query.where(AppReview.rating >= min_rating)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    reviews = result.scalars().all()

    return reviews


@router.get("/app-reviews/stats", response_model=List[AppReviewStatsResponse])
async def get_app_review_stats(
    db: AsyncSession = Depends(get_db)
):
    """앱별 리뷰 통계 (최적화된 단일 쿼리)"""
    # 기본 통계 쿼리 (앱별 총 리뷰 수, 평균 평점)
    base_stats_query = select(
        AppReview.app_name,
        func.count(AppReview.id).label('total_reviews'),
        func.avg(AppReview.rating).label('avg_rating')
    ).group_by(AppReview.app_name)

    base_result = await db.execute(base_stats_query)
    base_stats = {row.app_name: {
        'total_reviews': row.total_reviews,
        'avg_rating': round(float(row.avg_rating), 2) if row.avg_rating else 0
    } for row in base_result}

    # 평점 분포 쿼리 (앱별, 평점별 카운트)
    rating_dist_query = select(
        AppReview.app_name,
        AppReview.rating,
        func.count(AppReview.id).label('count')
    ).group_by(AppReview.app_name, AppReview.rating)

    rating_result = await db.execute(rating_dist_query)
    rating_dist = {}
    for row in rating_result:
        if row.app_name not in rating_dist:
            rating_dist[row.app_name] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        rating_dist[row.app_name][row.rating] = row.count

    # 플랫폼 분포 쿼리 (앱별, 플랫폼별 카운트)
    platform_dist_query = select(
        AppReview.app_name,
        AppReview.platform,
        func.count(AppReview.id).label('count')
    ).group_by(AppReview.app_name, AppReview.platform)

    platform_result = await db.execute(platform_dist_query)
    platform_dist = {}
    for row in platform_result:
        if row.app_name not in platform_dist:
            platform_dist[row.app_name] = {}
        platform_dist[row.app_name][row.platform] = row.count

    # 결과 조합
    stats_list = []
    for app_name, stats in base_stats.items():
        stats_list.append(AppReviewStatsResponse(
            app_name=app_name,
            total_reviews=stats['total_reviews'],
            average_rating=stats['avg_rating'],
            rating_distribution=rating_dist.get(app_name, {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}),
            platform_distribution=platform_dist.get(app_name, {})
        ))

    return stats_list


@router.post("/app-reviews/crawl")
async def crawl_app_reviews(
    db: AsyncSession = Depends(get_db)
):
    """앱 리뷰 크롤링 트리거"""
    try:
        from crawler.app_review_crawler import AppReviewCrawler

        crawler = AppReviewCrawler()
        await crawler.crawl_all_apps(max_reviews_per_app=100)

        return {
            "success": True,
            "message": "앱 리뷰 크롤링이 완료되었습니다."
        }
    except Exception as e:
        logger.error(f"앱 리뷰 크롤링 실패: {e}")
        return {
            "success": False,
            "message": f"크롤링 실패: {str(e)}"
        }


@router.get("/app-reviews/keywords")
async def get_app_review_keywords(
    app_name: Optional[str] = Query(None, description="앱 이름 필터"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """앱 리뷰에서 가장 많이 나온 키워드 추출"""
    try:
        # 리뷰 조회
        query = select(AppReview.review_text).where(AppReview.review_text.isnot(None))

        if app_name:
            query = query.where(AppReview.app_name == app_name)

        result = await db.execute(query)
        reviews = result.scalars().all()

        if not reviews:
            return []

        word_counter = Counter()

        # 불용어 리스트
        stopwords = {
            '그', '이', '저', '것', '수', '등', '들', '및', '를', '을', '가', '이', '은', '는', '하', '에', '의', '도', '로',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were',
            '있', '없', '되', '함', '하다', '있다', '없다', '같다', '와', '과', '네요', '요', '습니다', '이다'
        }

        for review_text in reviews:
            if not review_text:
                continue

            # 한글 단어 추출 (2자 이상)
            korean_words = re.findall(r'[가-힣]{2,}', review_text)
            # 영문 단어 추출 (2자 이상)
            english_words = re.findall(r'[a-zA-Z]{2,}', review_text.lower())

            # 단어 카운트
            for word in korean_words + english_words:
                if word not in stopwords and len(word) >= 2:
                    word_counter[word] += 1

        # 상위 N개 키워드 반환
        top_keywords = [
            {"keyword": word, "total_count": count}
            for word, count in word_counter.most_common(limit)
        ]

        return top_keywords

    except Exception as e:
        logger.error(f"리뷰 키워드 추출 실패: {e}")
        return []
