"""
최종 크롤링 테스트 - programming 갤러리
"""
import sys
import asyncio
sys.path.insert(0, '/Users/anipen/Desktop/monitoring/backend')

from crawler.dcinside_crawler import DCInsideCrawler

async def test():
    print("=" * 70)
    print("최종 크롤링 테스트")
    print("=" * 70)
    print()
    print("갤러리: programming (프로그래밍)")
    print("URL: https://gall.dcinside.com/board/lists?id=programming")
    print()
    
    crawler = DCInsideCrawler(gallery_id="programming")
    
    print("2페이지 크롤링 시작...")
    posts = await crawler.crawl_gallery(pages=2)
    
    print(f"\n✅ 총 {len(posts)}개 게시글 수집 완료!")
    
    if posts:
        print(f"\n처음 10개 게시글:")
        print("-" * 70)
        for i, post in enumerate(posts[:10], 1):
            print(f"{i}. [{post.post_id}] {post.title[:60]}")
            print(f"   조회: {post.view_count} | 추천: {post.recommend_count} | 댓글: {post.comment_count}")
        print("-" * 70)
        print(f"\n✅ 크롤러가 정상 작동합니다!")
    else:
        print("\n❌ 게시글을 수집하지 못했습니다.")

asyncio.run(test())
