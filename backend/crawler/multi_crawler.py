"""
여러 갤러리/게시판을 통합 크롤링하는 모듈
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from typing import List
import logging

from config import get_settings
from crawler.dcinside_crawler import DCInsideCrawler, CrawledPost as DCPost
from crawler.arcalive_crawler import ArcaliveCrawler, CrawledPost as ArcaPost

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def crawl_all_targets(pages: int = None) -> List:
    """모든 설정된 갤러리/게시판 크롤링"""
    settings = get_settings()
    pages = pages or settings.max_pages_per_crawl
    
    all_posts = []
    
    logger.info("="*70)
    logger.info("통합 크롤링 시작")
    logger.info(f"대상: {len(settings.target_galleries)}개 갤러리")
    logger.info("="*70)
    
    for gallery_config in settings.target_galleries:
        gallery_id = gallery_config['id']
        gallery_name = gallery_config['name']
        gallery_type = gallery_config['type']
        
        logger.info(f"\n[{gallery_name}] 크롤링 시작...")
        
        try:
            if gallery_type == 'dcinside_minor':
                # 디시인사이드 마이너갤러리
                crawler = DCInsideCrawler(gallery_id=gallery_id, is_minor=True)
                posts = await crawler.crawl_gallery(pages=pages)
                all_posts.extend(posts)
                logger.info(f"✅ [{gallery_name}] {len(posts)}개 수집 완료")
                
            elif gallery_type == 'dcinside':
                # 디시인사이드 일반갤러리
                crawler = DCInsideCrawler(gallery_id=gallery_id, is_minor=False)
                posts = await crawler.crawl_gallery(pages=pages)
                all_posts.extend(posts)
                logger.info(f"✅ [{gallery_name}] {len(posts)}개 수집 완료")
                
            elif gallery_type == 'arcalive':
                # 아카라이브
                crawler = ArcaliveCrawler(board_id=gallery_id)
                posts = await crawler.crawl_board(pages=pages)
                all_posts.extend(posts)
                logger.info(f"✅ [{gallery_name}] {len(posts)}개 수집 완료")
                
            else:
                logger.warning(f"⚠️  [{gallery_name}] 지원하지 않는 타입: {gallery_type}")
            
            # Rate limiting between galleries
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ [{gallery_name}] 크롤링 실패: {e}")
            continue
    
    logger.info("="*70)
    logger.info(f"통합 크롤링 완료: 총 {len(all_posts)}개 게시글 수집")
    logger.info("="*70)
    
    return all_posts


# 테스트용
if __name__ == "__main__":
    async def test():
        posts = await crawl_all_targets(pages=2)
        print(f"\n수집된 게시글:")
        for i, post in enumerate(posts[:10], 1):
            print(f"{i}. [{post.gallery_id}] {post.title[:50]}")
    
    asyncio.run(test())
