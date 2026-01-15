"""
캐릭터챗 서비스 통합 크롤러
"""
import asyncio
from typing import Dict, List
import logging

from .zeta_crawler import ZetaCrawler, CharacterData as ZetaCharacterData
from .babechat_crawler import BabeChatCrawler, CharacterData as BabeChatCharacterData
from .lunatalk_crawler import LunaTalkCrawler, CharacterData as LunaTalkCharacterData

logger = logging.getLogger(__name__)


async def crawl_all_character_services(services: List[str] = None) -> Dict[str, List]:
    """
    모든 캐릭터챗 서비스 크롤링
    
    Args:
        services: 크롤링할 서비스 목록 ['zeta', 'babechat', 'lunatalk']
                 None이면 모든 서비스 크롤링
    
    Returns:
        {'zeta': [CharacterData, ...], 'babechat': [CharacterData, ...], 'lunatalk': [CharacterData, ...]}
    """
    if services is None:
        services = ['zeta', 'lunatalk']  # 기본: 제타, 루나톡
    
    logger.info(f"캐릭터 서비스 크롤링 시작: {services}")
    
    results = {}
    
    # 제타 크롤링
    if 'zeta' in services:
        try:
            crawler = ZetaCrawler()
            zeta_results = await crawler.crawl_rankings(30)
            results['zeta'] = zeta_results
            logger.info(f"zeta 크롤링 완료: {len(zeta_results)}개")
        except Exception as e:
            logger.error(f"zeta 크롤링 실패: {e}")
            results['zeta'] = []
    
    # 루나톡 크롤링
    if 'lunatalk' in services:
        try:
            crawler = LunaTalkCrawler()
            # 일간 랭킹 크롤링
            lunatalk_results = await crawler.crawl_rankings(30, period="daily")
            results['lunatalk'] = lunatalk_results
            logger.info(f"lunatalk 크롤링 완료: {len(lunatalk_results)}개")
        except Exception as e:
            logger.error(f"lunatalk 크롤링 실패: {e}")
            results['lunatalk'] = []
    
    # 베이비챗은 현재 미지원 (JavaScript 렌더링 필요)
    if 'babechat' in services:
        logger.warning("babechat은 현재 지원되지 않습니다 (JavaScript 렌더링 필요)")
        results['babechat'] = []
    
    total_count = sum(len(chars) for chars in results.values())
    logger.info(f"전체 크롤링 완료: {total_count}개 캐릭터 수집")
    
    return results
