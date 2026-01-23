"""
뉴스 크롤러
구글 뉴스 RSS 기반 수집
"""
from typing import Dict, List
import logging

from .google_news_crawler import GoogleNewsCrawler, NewsArticleData

logger = logging.getLogger(__name__)


async def crawl_all_news(
    keywords: List[str] = None,
    limit_per_keyword: int = 20,
    **kwargs  # 호환성을 위해 추가 인자 무시
) -> Dict[str, List]:
    """
    구글 뉴스에서 기사 수집
    
    Args:
        keywords: 검색 키워드 목록 (None이면 설정에서 가져옴)
        limit_per_keyword: 키워드당 최대 결과 개수
    
    Returns:
        {'google': [NewsArticleData, ...]}
    """
    logger.info("뉴스 크롤링 시작 (구글 뉴스)")
    
    results = {}
    
    try:
        crawler = GoogleNewsCrawler()
        google_results = await crawler.crawl_all_keywords(
            keywords=keywords,
            limit_per_keyword=limit_per_keyword
        )
        results['google'] = google_results
        logger.info(f"✅ 구글 뉴스 크롤링 완료: {len(google_results)}개")
    except Exception as e:
        logger.error(f"❌ 구글 뉴스 크롤링 실패: {e}")
        results['google'] = []
    
    total_count = len(results.get('google', []))
    logger.info(f"전체 뉴스 크롤링 완료: {total_count}개 기사 수집")
    
    return results
