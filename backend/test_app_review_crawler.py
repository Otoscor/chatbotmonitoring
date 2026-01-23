"""
앱 리뷰 크롤러 테스트
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from crawler.app_review_crawler import AppReviewCrawler


async def test_single_app():
    """단일 앱 테스트 (Character AI)"""
    crawler = AppReviewCrawler()
    
    print("=" * 70)
    print("앱 리뷰 크롤러 테스트 시작")
    print("대상: Character AI (구글 플레이만, 5개 리뷰)")
    print("=" * 70)
    
    # Character AI 구글 플레이 리뷰 테스트
    reviews = await crawler.crawl_google_play_reviews(
        'ai.character.app',
        'Character AI',
        max_reviews=5
    )
    
    if reviews:
        print(f"\n✅ 수집된 리뷰: {len(reviews)}개")
        print("\n--- 샘플 리뷰 ---")
        for i, review in enumerate(reviews[:3], 1):
            print(f"\n{i}. 평점: {review['rating']}/5")
            print(f"   리뷰어: {review['reviewer_name']}")
            print(f"   내용: {review['review_text'][:100]}...")
        
        # 데이터베이스 저장 테스트
        print("\n💾 데이터베이스 저장 테스트...")
        await crawler.save_reviews(reviews)
        print("✅ 저장 완료")
    else:
        print("❌ 리뷰 수집 실패")


if __name__ == "__main__":
    asyncio.run(test_single_app())
