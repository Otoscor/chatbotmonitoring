"""
크롤러 직접 테스트
"""
import sys
import asyncio
sys.path.insert(0, '/Users/anipen/Desktop/monitoring/backend')

from crawler.dcinside_crawler import DCInsideCrawler

async def test_crawl():
    print("=" * 60)
    print("크롤러 테스트 시작")
    print("=" * 60)
    
    # chatbot 갤러리 테스트
    gallery_id = "chatbot"
    print(f"\n테스트 갤러리: {gallery_id}")
    print(f"URL: https://gall.dcinside.com/board/lists?id={gallery_id}")
    
    crawler = DCInsideCrawler(gallery_id=gallery_id)
    
    try:
        print("\n1페이지만 크롤링 시도 중...")
        posts = await crawler.crawl_gallery(pages=1)
        
        print(f"\n수집 결과: {len(posts)}개 게시글")
        
        if posts:
            print("\n첫 5개 게시글:")
            for i, post in enumerate(posts[:5], 1):
                print(f"\n{i}. [{post.post_id}] {post.title}")
                print(f"   작성자: {post.author or '익명'}")
                print(f"   조회: {post.view_count}, 추천: {post.recommend_count}")
                print(f"   URL: {post.url}")
        else:
            print("\n⚠️ 게시글을 수집하지 못했습니다.")
            print("디버깅 정보:")
            print(f"  - 갤러리 ID: {crawler.gallery_id}")
            print(f"  - Base URL: {crawler.BASE_URL}")
            print(f"  - Delay: {crawler.delay}초")
            
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crawl())
