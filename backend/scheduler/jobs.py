"""
스케줄러 작업 정의
- 일일 자동 크롤링
- 리포트 생성
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import get_settings
from models.database import get_db_session, Post, DailyReport
from crawler.dcinside_crawler import run_crawler
from analyzer.trend_analyzer import generate_daily_report
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


async def daily_crawl_job():
    """
    일일 크롤링 작업
    - 매일 자정에 실행
    - 갤러리 크롤링 후 DB 저장
    """
    logger.info("=== 일일 크롤링 작업 시작 ===")
    
    try:
        # 크롤링 실행
        posts = await run_crawler(pages=settings.max_pages_per_crawl)
        logger.info(f"크롤링 완료: {len(posts)}개 게시글 수집")
        
        # DB에 저장
        async with get_db_session() as session:
            saved_count = 0
            for post_data in posts:
                # 중복 체크
                existing = await session.execute(
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
                session.add(post)
                saved_count += 1
            
            await session.commit()
            logger.info(f"DB 저장 완료: {saved_count}개 신규 게시글")
        
        logger.info("=== 일일 크롤링 작업 완료 ===")
        
    except Exception as e:
        logger.error(f"크롤링 작업 실패: {e}")


async def daily_report_job():
    """
    일일 리포트 생성 작업
    - 크롤링 완료 후 실행
    """
    logger.info("=== 일일 리포트 생성 시작 ===")
    
    try:
        today = datetime.now()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        async with get_db_session() as session:
            # 오늘 게시글 조회
            query = select(Post).where(
                Post.crawled_at >= start_of_day,
                Post.crawled_at < end_of_day
            )
            result = await session.execute(query)
            posts = result.scalars().all()
            
            if not posts:
                logger.warning("오늘 수집된 게시글이 없습니다")
                return
            
            logger.info(f"오늘 게시글: {len(posts)}개")
            
            # 어제 게시글 조회 (비교용)
            prev_start = start_of_day - timedelta(days=1)
            prev_query = select(Post).where(
                Post.crawled_at >= prev_start,
                Post.crawled_at < start_of_day
            )
            prev_result = await session.execute(prev_query)
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
            
            report_data = generate_daily_report(posts_dict, prev_posts_dict, today)
            
            # 기존 리포트 확인
            existing_query = select(DailyReport).where(
                DailyReport.report_date >= start_of_day,
                DailyReport.report_date < end_of_day
            )
            existing = await session.execute(existing_query)
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
                logger.info("기존 리포트 업데이트 완료")
            else:
                # 새로 생성
                new_report = DailyReport(
                    report_date=today,
                    total_posts=report_data["statistics"]["total_posts"],
                    total_views=report_data["statistics"]["total_views"],
                    total_recommends=report_data["statistics"]["total_recommends"],
                    total_comments=report_data["statistics"]["total_comments"],
                    top_keywords=report_data["top_keywords"],
                    top_characters=report_data["character_rankings"],
                    trending_topics=report_data["trending_topics"]
                )
                session.add(new_report)
                logger.info("신규 리포트 생성 완료")
            
            await session.commit()
        
        logger.info("=== 일일 리포트 생성 완료 ===")
        
    except Exception as e:
        logger.error(f"리포트 생성 실패: {e}")


def create_scheduler() -> AsyncIOScheduler:
    """스케줄러 생성 및 작업 등록"""
    scheduler = AsyncIOScheduler()
    
    # 매일 자정 크롤링 (00:00)
    scheduler.add_job(
        daily_crawl_job,
        CronTrigger(hour=0, minute=0),
        id="daily_crawl",
        name="일일 크롤링",
        replace_existing=True
    )
    
    # 매일 00:30 리포트 생성 (크롤링 완료 후)
    scheduler.add_job(
        daily_report_job,
        CronTrigger(hour=0, minute=30),
        id="daily_report",
        name="일일 리포트 생성",
        replace_existing=True
    )
    
    logger.info("스케줄러 작업 등록 완료")
    logger.info("- 일일 크롤링: 매일 00:00")
    logger.info("- 일일 리포트: 매일 00:30")
    
    return scheduler


async def run_scheduler():
    """스케줄러 실행"""
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("스케줄러 시작됨")
    
    try:
        # 무한 대기
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("스케줄러 종료됨")


if __name__ == "__main__":
    # 단독 실행 시
    asyncio.run(run_scheduler())
