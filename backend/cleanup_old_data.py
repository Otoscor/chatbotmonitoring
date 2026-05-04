"""
오래된 데이터 정리 스크립트

데이터베이스에서 설정된 기간보다 오래된 데이터를 삭제합니다.
- 게시글: 90일 이상 오래된 데이터
- 리포트: 180일 이상 오래된 데이터
- 캐릭터 서비스: 30일 이상 오래된 데이터
- 뉴스: 60일 이상 오래된 데이터
- 앱 리뷰: 90일 이상 오래된 데이터
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, delete
from models.database import (
    get_db_session,
    Post,
    DailyReport,
    ChatServiceCharacter,
    NewsArticle,
    AppReview
)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def cleanup_old_data(
    posts_days: int = 90,
    reports_days: int = 180,
    characters_days: int = 30,
    news_days: int = 60,
    reviews_days: int = 90,
    dry_run: bool = False
):
    """
    오래된 데이터 정리
    
    Args:
        posts_days: 게시글 보관 기간 (일)
        reports_days: 리포트 보관 기간 (일)
        characters_days: 캐릭터 서비스 데이터 보관 기간 (일)
        news_days: 뉴스 기사 보관 기간 (일)
        reviews_days: 앱 리뷰 보관 기간 (일)
        dry_run: True면 삭제 없이 조회만 수행
    """
    async with get_db_session() as session:
        try:
            logger.info("=" * 70)
            logger.info("오래된 데이터 정리 시작")
            logger.info(f"실행 모드: {'DRY RUN (조회만)' if dry_run else '실제 삭제'}")
            logger.info("=" * 70)
            
            total_deleted = 0
            
            # 1. 오래된 게시글 삭제
            if posts_days:
                cutoff = datetime.now() - timedelta(days=posts_days)
                logger.info(f"\n[게시글] {posts_days}일 이전 데이터 정리 (기준: {cutoff.strftime('%Y-%m-%d %H:%M:%S')})")
                
                # 삭제 대상 카운트
                count_query = select(Post).where(Post.crawled_at < cutoff)
                result = await session.execute(count_query)
                old_posts = result.scalars().all()
                count = len(old_posts)
                
                if count > 0:
                    logger.info(f"  삭제 대상: {count}개")
                    if not dry_run:
                        delete_query = delete(Post).where(Post.crawled_at < cutoff)
                        await session.execute(delete_query)
                        await session.commit()
                        logger.info(f"  ✅ {count}개 게시글 삭제 완료")
                        total_deleted += count
                else:
                    logger.info("  삭제 대상 없음")
            
            # 2. 오래된 리포트 삭제
            if reports_days:
                cutoff = datetime.now() - timedelta(days=reports_days)
                logger.info(f"\n[리포트] {reports_days}일 이전 데이터 정리 (기준: {cutoff.strftime('%Y-%m-%d %H:%M:%S')})")
                
                count_query = select(DailyReport).where(DailyReport.report_date < cutoff)
                result = await session.execute(count_query)
                old_reports = result.scalars().all()
                count = len(old_reports)
                
                if count > 0:
                    logger.info(f"  삭제 대상: {count}개")
                    if not dry_run:
                        delete_query = delete(DailyReport).where(DailyReport.report_date < cutoff)
                        await session.execute(delete_query)
                        await session.commit()
                        logger.info(f"  ✅ {count}개 리포트 삭제 완료")
                        total_deleted += count
                else:
                    logger.info("  삭제 대상 없음")
            
            # 3. 오래된 캐릭터 서비스 데이터 삭제
            if characters_days:
                cutoff = datetime.now() - timedelta(days=characters_days)
                logger.info(f"\n[캐릭터 서비스] {characters_days}일 이전 데이터 정리 (기준: {cutoff.strftime('%Y-%m-%d %H:%M:%S')})")
                
                count_query = select(ChatServiceCharacter).where(ChatServiceCharacter.crawled_at < cutoff)
                result = await session.execute(count_query)
                old_chars = result.scalars().all()
                count = len(old_chars)
                
                if count > 0:
                    logger.info(f"  삭제 대상: {count}개")
                    if not dry_run:
                        delete_query = delete(ChatServiceCharacter).where(ChatServiceCharacter.crawled_at < cutoff)
                        await session.execute(delete_query)
                        await session.commit()
                        logger.info(f"  ✅ {count}개 캐릭터 데이터 삭제 완료")
                        total_deleted += count
                else:
                    logger.info("  삭제 대상 없음")
            
            # 4. 오래된 뉴스 기사 삭제
            if news_days:
                cutoff = datetime.now() - timedelta(days=news_days)
                logger.info(f"\n[뉴스] {news_days}일 이전 데이터 정리 (기준: {cutoff.strftime('%Y-%m-%d %H:%M:%S')})")
                
                count_query = select(NewsArticle).where(NewsArticle.crawled_at < cutoff)
                result = await session.execute(count_query)
                old_news = result.scalars().all()
                count = len(old_news)
                
                if count > 0:
                    logger.info(f"  삭제 대상: {count}개")
                    if not dry_run:
                        delete_query = delete(NewsArticle).where(NewsArticle.crawled_at < cutoff)
                        await session.execute(delete_query)
                        await session.commit()
                        logger.info(f"  ✅ {count}개 뉴스 기사 삭제 완료")
                        total_deleted += count
                else:
                    logger.info("  삭제 대상 없음")
            
            # 5. 오래된 앱 리뷰 삭제
            if reviews_days:
                cutoff = datetime.now() - timedelta(days=reviews_days)
                logger.info(f"\n[앱 리뷰] {reviews_days}일 이전 데이터 정리 (기준: {cutoff.strftime('%Y-%m-%d %H:%M:%S')})")
                
                count_query = select(AppReview).where(AppReview.crawled_at < cutoff)
                result = await session.execute(count_query)
                old_reviews = result.scalars().all()
                count = len(old_reviews)
                
                if count > 0:
                    logger.info(f"  삭제 대상: {count}개")
                    if not dry_run:
                        delete_query = delete(AppReview).where(AppReview.crawled_at < cutoff)
                        await session.execute(delete_query)
                        await session.commit()
                        logger.info(f"  ✅ {count}개 앱 리뷰 삭제 완료")
                        total_deleted += count
                else:
                    logger.info("  삭제 대상 없음")
            
            logger.info("\n" + "=" * 70)
            if dry_run:
                logger.info(f"DRY RUN 완료: 총 {total_deleted}개 항목이 삭제 대상입니다")
            else:
                logger.info(f"정리 완료: 총 {total_deleted}개 항목 삭제됨")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"오류 발생: {e}")
            await session.rollback()
            raise


async def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="오래된 데이터 정리")
    parser.add_argument("--posts-days", type=int, default=90, help="게시글 보관 기간 (기본: 90일)")
    parser.add_argument("--reports-days", type=int, default=180, help="리포트 보관 기간 (기본: 180일)")
    parser.add_argument("--characters-days", type=int, default=30, help="캐릭터 서비스 보관 기간 (기본: 30일)")
    parser.add_argument("--news-days", type=int, default=60, help="뉴스 보관 기간 (기본: 60일)")
    parser.add_argument("--reviews-days", type=int, default=90, help="앱 리뷰 보관 기간 (기본: 90일)")
    parser.add_argument("--dry-run", action="store_true", help="실제 삭제 없이 조회만 수행")
    
    args = parser.parse_args()
    
    await cleanup_old_data(
        posts_days=args.posts_days,
        reports_days=args.reports_days,
        characters_days=args.characters_days,
        news_days=args.news_days,
        reviews_days=args.reviews_days,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    asyncio.run(main())
