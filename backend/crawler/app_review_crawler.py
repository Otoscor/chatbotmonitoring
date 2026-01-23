"""
앱 리뷰 크롤러
구글 플레이스토어와 앱스토어에서 앱 리뷰를 수집
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import logging

from google_play_scraper import reviews_all, Sort
from app_store_scraper import AppStore

from config import get_settings
from models.database import AppReview, get_db_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppReviewCrawler:
    """앱 리뷰 크롤러"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def _generate_review_id(self, platform: str, app_name: str, reviewer: str, date: str, text: str) -> str:
        """리뷰 고유 ID 생성"""
        unique_str = f"{platform}_{app_name}_{reviewer}_{date}_{text[:100]}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    async def crawl_google_play_reviews(self, app_id: str, app_name: str, max_reviews: int = 100) -> List[Dict]:
        """구글 플레이스토어 리뷰 크롤링"""
        logger.info(f"[{app_name}] 구글 플레이 리뷰 크롤링 시작... (앱 ID: {app_id})")
        
        try:
            # 동기 함수를 비동기로 실행
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: reviews_all(
                    app_id,
                    sleep_milliseconds=1000,
                    lang='ko',
                    country='kr',
                    sort=Sort.NEWEST
                )
            )
            
            # 최대 개수 제한
            if len(result) > max_reviews:
                result = result[:max_reviews]
            
            reviews_data = []
            for review in result:
                review_id = self._generate_review_id(
                    'google_play',
                    app_name,
                    review.get('userName', 'unknown'),
                    str(review.get('at', '')),
                    review.get('content', '')
                )
                
                review_data = {
                    'review_id': review_id,
                    'app_name': app_name,
                    'platform': 'google_play',
                    'review_text': review.get('content'),
                    'rating': review.get('score', 0),
                    'reviewer_name': review.get('userName'),
                    'review_date': review.get('at'),
                    'extra_data': {
                        'thumbsUpCount': review.get('thumbsUpCount', 0),
                        'replyContent': review.get('replyContent'),
                        'appVersion': review.get('appVersion'),
                        'reviewCreatedVersion': review.get('reviewCreatedVersion')
                    }
                }
                reviews_data.append(review_data)
            
            logger.info(f"[{app_name}] ✅ 구글 플레이 리뷰 {len(reviews_data)}개 수집 완료")
            return reviews_data
            
        except Exception as e:
            logger.error(f"[{app_name}] ❌ 구글 플레이 리뷰 크롤링 실패: {e}")
            return []
    
    async def crawl_app_store_reviews(self, app_id: str, app_name_slug: str, app_display_name: str, 
                                     country: str = 'kr', max_reviews: int = 100) -> List[Dict]:
        """앱스토어 리뷰 크롤링"""
        logger.info(f"[{app_display_name}] 앱스토어 리뷰 크롤링 시작... (앱 ID: {app_id})")
        
        try:
            # AppStore 객체 생성 및 리뷰 수집
            app = AppStore(country=country, app_name=app_name_slug, app_id=app_id)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, app.review, max_reviews)
            
            reviews_data = []
            for review in app.reviews:
                review_id = self._generate_review_id(
                    'app_store',
                    app_display_name,
                    review.get('userName', 'unknown'),
                    str(review.get('date', '')),
                    review.get('review', '')
                )
                
                review_data = {
                    'review_id': review_id,
                    'app_name': app_display_name,
                    'platform': 'app_store',
                    'review_text': review.get('review'),
                    'rating': review.get('rating', 0),
                    'reviewer_name': review.get('userName'),
                    'review_date': review.get('date'),
                    'extra_data': {
                        'title': review.get('title'),
                        'isEdited': review.get('isEdited', False)
                    }
                }
                reviews_data.append(review_data)
            
            logger.info(f"[{app_display_name}] ✅ 앱스토어 리뷰 {len(reviews_data)}개 수집 완료")
            return reviews_data
            
        except Exception as e:
            logger.error(f"[{app_display_name}] ❌ 앱스토어 리뷰 크롤링 실패: {e}")
            return []
    
    async def save_reviews(self, reviews_data: List[Dict]):
        """리뷰 데이터 저장"""
        if not reviews_data:
            return
        
        async with get_db_session() as session:
            saved_count = 0
            skipped_count = 0
            
            for review_data in reviews_data:
                try:
                    # 중복 체크
                    from sqlalchemy import select
                    stmt = select(AppReview).where(AppReview.review_id == review_data['review_id'])
                    result = await session.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # 새 리뷰 저장
                    review = AppReview(**review_data)
                    session.add(review)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"리뷰 저장 실패: {e}")
                    continue
            
            await session.commit()
            logger.info(f"💾 저장: {saved_count}개 | 중복 스킵: {skipped_count}개")
    
    async def crawl_all_apps(self, max_reviews_per_app: int = 100):
        """모든 설정된 앱의 리뷰 크롤링"""
        logger.info("=" * 70)
        logger.info("앱 리뷰 통합 크롤링 시작")
        logger.info(f"대상: {len(self.settings.target_apps)}개 앱")
        logger.info("=" * 70)
        
        total_reviews = 0
        
        for app_config in self.settings.target_apps:
            app_name = app_config['name']
            logger.info(f"\n[{app_name}] 크롤링 시작...")
            
            all_reviews = []
            
            # 구글 플레이 리뷰
            if app_config.get('google_play_id'):
                google_reviews = await self.crawl_google_play_reviews(
                    app_config['google_play_id'],
                    app_name,
                    max_reviews_per_app
                )
                all_reviews.extend(google_reviews)
                await asyncio.sleep(2)  # Rate limiting
            
            # 앱스토어 리뷰
            if app_config.get('app_store_id'):
                app_store_reviews = await self.crawl_app_store_reviews(
                    app_config['app_store_id'],
                    app_config.get('app_store_name', app_name.lower()),
                    app_name,
                    app_config.get('country', 'kr'),
                    max_reviews_per_app
                )
                all_reviews.extend(app_store_reviews)
                await asyncio.sleep(2)  # Rate limiting
            
            # 저장
            await self.save_reviews(all_reviews)
            total_reviews += len(all_reviews)
            
            logger.info(f"[{app_name}] 총 {len(all_reviews)}개 리뷰 처리 완료\n")
        
        logger.info("=" * 70)
        logger.info(f"통합 크롤링 완료: 총 {total_reviews}개 리뷰 수집")
        logger.info("=" * 70)


# 테스트용
if __name__ == "__main__":
    async def test():
        crawler = AppReviewCrawler()
        await crawler.crawl_all_apps(max_reviews_per_app=50)
    
    asyncio.run(test())
