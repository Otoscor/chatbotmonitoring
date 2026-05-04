"""
크롤링 API 라우트
"""
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, Post, DailyReport
from api.schemas.common import CrawlRequest, CrawlResponse
from api.utils.date_utils import get_day_boundaries
from crawler.multi_crawler import crawl_all_targets
from analyzer.trend_analyzer import generate_daily_report

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/crawl", response_model=CrawlResponse)
async def trigger_crawl(
    request: CrawlRequest,
    db: AsyncSession = Depends(get_db)
):
    """수동 크롤링 트리거 - 모든 갤러리"""
    try:
        posts = await crawl_all_targets(pages=request.pages)

        # DB에 저장
        saved_count = 0
        for post_data in posts:
            # 중복 체크
            existing = await db.execute(
                select(Post).where(Post.post_id == post_data.post_id)
            )
            if existing.scalar_one_or_none():
                continue

            post = Post(
                post_id=post_data.post_id,
                gallery_id=post_data.gallery_id,
                title=post_data.title,
                author=post_data.author,
                created_at=post_data.created_at,
                view_count=post_data.view_count,
                recommend_count=post_data.recommend_count,
                comment_count=post_data.comment_count,
                url=post_data.url
            )
            db.add(post)
            saved_count += 1

        await db.commit()

        return CrawlResponse(
            success=True,
            message=f"크롤링 완료: {len(posts)}개 수집, {saved_count}개 저장",
            posts_count=saved_count
        )
    except Exception as e:
        logger.error(f"크롤링 실패: {e}")
        return CrawlResponse(
            success=False,
            message=f"크롤링 실패: {str(e)}",
            posts_count=0
        )


@router.post("/reports/generate")
async def generate_report(
    date: str = None,
    db: AsyncSession = Depends(get_db)
):
    """수동 리포트 생성"""
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")

        start_of_day, end_of_day = get_day_boundaries(target_date)

        query = select(Post).where(
            Post.crawled_at >= start_of_day,
            Post.crawled_at < end_of_day
        )
        result = await db.execute(query)
        posts = result.scalars().all()

        if not posts:
            raise HTTPException(status_code=404, detail="해당 날짜의 게시글이 없습니다")
    else:
        since = datetime.now() - timedelta(hours=24)
        query = select(Post).where(
            Post.crawled_at >= since
        )
        result = await db.execute(query)
        posts = result.scalars().all()

        if not posts:
            raise HTTPException(status_code=404, detail="최근 24시간 이내 크롤링된 게시글이 없습니다")

        target_date = datetime.now()
        start_of_day, end_of_day = get_day_boundaries(target_date)

    # 이전 날짜 게시글 (비교용)
    prev_start = start_of_day - timedelta(days=1)
    prev_query = select(Post).where(
        Post.crawled_at >= prev_start,
        Post.crawled_at < start_of_day
    )
    prev_result = await db.execute(prev_query)
    prev_posts = prev_result.scalars().all()

    # 리포트 생성
    posts_dict = [
        {
            "title": p.title,
            "view_count": p.view_count,
            "recommend_count": p.recommend_count,
            "comment_count": p.comment_count
        }
        for p in posts
    ]
    prev_posts_dict = [
        {
            "title": p.title,
            "view_count": p.view_count,
            "recommend_count": p.recommend_count,
            "comment_count": p.comment_count
        }
        for p in prev_posts
    ]

    report_data = generate_daily_report(posts_dict, prev_posts_dict, target_date)

    # 기존 리포트 확인
    existing_query = select(DailyReport).where(
        DailyReport.report_date >= start_of_day,
        DailyReport.report_date < end_of_day
    )
    existing = await db.execute(existing_query)
    existing_report = existing.scalar_one_or_none()

    if existing_report:
        # 업데이트
        existing_report.total_posts = report_data["statistics"]["total_posts"]
        existing_report.total_views = report_data["statistics"]["total_views"]
        existing_report.total_recommends = report_data["statistics"]["total_recommends"]
        existing_report.total_comments = report_data["statistics"]["total_comments"]
        existing_report.top_keywords = report_data["top_keywords"]
        existing_report.top_characters = report_data["character_rankings"]
        existing_report.trending_topics = report_data["trending_topics"]
    else:
        # 새로 생성
        new_report = DailyReport(
            report_date=target_date,
            total_posts=report_data["statistics"]["total_posts"],
            total_views=report_data["statistics"]["total_views"],
            total_recommends=report_data["statistics"]["total_recommends"],
            total_comments=report_data["statistics"]["total_comments"],
            top_keywords=report_data["top_keywords"],
            top_characters=report_data["character_rankings"],
            trending_topics=report_data["trending_topics"]
        )
        db.add(new_report)

    await db.commit()

    return {
        "success": True,
        "message": "리포트 생성 완료",
        "report": report_data
    }
