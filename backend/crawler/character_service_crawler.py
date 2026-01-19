"""
캐릭터챗 서비스 통합 크롤러
"""
import asyncio
from typing import Dict, List
import logging

from .zeta_crawler import ZetaCrawler, CharacterData as ZetaCharacterData
from .babechat_crawler import BabeChatCrawler, CharacterData as BabeChatCharacterData
from .lunatalk_crawler import LunaTalkCrawler, CharacterData as LunaTalkCharacterData
from .crack_crawler import CrackCrawler, CharacterData as CrackCharacterData

logger = logging.getLogger(__name__)


async def crawl_all_character_services(services: List[str] = None) -> Dict[str, List]:
    """
    모든 캐릭터챗 서비스 크롤링
    
    Args:
        services: 크롤링할 서비스 목록 ['zeta', 'babechat', 'lunatalk', 'crack']
                 None이면 모든 서비스 크롤링
    
    Returns:
        {'zeta': [CharacterData, ...], 'babechat': [CharacterData, ...], 'lunatalk': [CharacterData, ...], 'crack': [CharacterData, ...]}
    """
    if services is None:
        services = ['zeta', 'lunatalk', 'babechat', 'crack']  # 기본: 제타, 루나톡, 베이비챗, 크랙
    
    logger.info(f"캐릭터 서비스 크롤링 시작: {services}")
    
    results = {}
    
    # 제타 크롤링
    if 'zeta' in services:
        try:
            crawler = ZetaCrawler()
            zeta_results = await crawler.crawl_rankings(30)
            results['zeta'] = zeta_results
            logger.info(f"✅ zeta 크롤링 완료: {len(zeta_results)}개")
        except Exception as e:
            logger.error(f"❌ zeta 크롤링 실패: {e}")
            results['zeta'] = []
    
    # 루나톡 크롤링
    if 'lunatalk' in services:
        try:
            crawler = LunaTalkCrawler()
            # 일간 랭킹 크롤링
            lunatalk_results = await crawler.crawl_rankings(30, period="daily")
            results['lunatalk'] = lunatalk_results
            logger.info(f"✅ lunatalk 크롤링 완료: {len(lunatalk_results)}개")
        except Exception as e:
            logger.error(f"❌ lunatalk 크롤링 실패: {e}")
            results['lunatalk'] = []
    
    # 베이비챗 크롤링 (API 기반)
    if 'babechat' in services:
        try:
            crawler = BabeChatCrawler()
            babechat_results = await crawler.crawl_rankings(30)
            results['babechat'] = babechat_results
            logger.info(f"✅ babechat 크롤링 완료: {len(babechat_results)}개")
        except Exception as e:
            logger.error(f"❌ babechat 크롤링 실패: {e}")
            results['babechat'] = []
    
    # 크랙 크롤링 (__NEXT_DATA__ 기반)
    if 'crack' in services:
        try:
            crawler = CrackCrawler()
            crack_results = await crawler.crawl_rankings(30)
            results['crack'] = crack_results
            logger.info(f"✅ crack 크롤링 완료: {len(crack_results)}개")
        except Exception as e:
            logger.error(f"❌ crack 크롤링 실패: {e}")
            results['crack'] = []
    
    total_count = sum(len(chars) for chars in results.values())
    logger.info(f"전체 크롤링 완료: {total_count}개 캐릭터 수집")
    
    return results
