"""
제타(Zeta) AI 캐릭터 크롤러
"""
import asyncio
import re
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
import logging

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


@dataclass
class CharacterData:
    """캐릭터 데이터"""
    character_id: str
    rank: int
    name: str
    author: Optional[str]
    views: int
    tags: Optional[List[str]]
    description: Optional[str]
    thumbnail_url: Optional[str]
    character_url: Optional[str]


class ZetaCrawler:
    """제타 AI 크롤러"""
    BASE_URL = "https://zeta-ai.io"
    RANKING_URL = f"{BASE_URL}/ko"
    
    def __init__(self):
        self.ua = UserAgent()
        self.delay = 1.5
        self.max_retries = 3
    
    async def _fetch_html(self, url: str) -> Optional[str]:
        """HTML 가져오기"""
        headers = {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    await asyncio.sleep(self.delay)
                    return response.text
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 오류 {url}: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"요청 오류 {url}: {e}")
            except Exception as e:
                logger.error(f"예상치 못한 오류 {url}: {e}")
            
            if attempt < self.max_retries - 1:
                logger.warning(f"재시도 중... ({attempt + 1}/{self.max_retries})")
                await asyncio.sleep(self.delay * (attempt + 1))
        
        return None
    
    def _parse_views(self, view_text: str) -> int:
        """조회수 파싱 (예: "3,884만" -> 38840000, "24.2만" -> 242000)"""
        try:
            view_text = view_text.replace(",", "").strip()
            
            if "만" in view_text:
                number = float(view_text.replace("만", ""))
                return int(number * 10000)
            
            if "천" in view_text:
                number = float(view_text.replace("천", ""))
                return int(number * 1000)
            
            return int(view_text)
        except ValueError:
            logger.warning(f"조회수 파싱 실패: {view_text}")
            return 0
    
    def _extract_character_id(self, url: str) -> str:
        """URL에서 캐릭터 ID 추출"""
        match = re.search(r'/plots/([^/]+)/profile', url)
        if match:
            return match.group(1)
        return url
    
    async def crawl_rankings(self, limit: int = 30) -> List[CharacterData]:
        """인기 캐릭터 순위 크롤링 (API 사용)"""
        logger.info(f"제타 크롤링 시작 (상위 {limit}개)")
        
        # API 엔드포인트 및 파라미터
        api_url = "https://api.zeta-ai.io/v1/plots/ranking"
        params = {
            "limit": limit,
            "genres": "ALL",
            "type": "TRENDING",
            "filterType": "GENRE",
            "filterValues": "all"
        }
        
        headers = {
            "User-Agent": self.ua.random,
            "Accept": "application/json",
            "Referer": "https://zeta-ai.io/"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url, params=params, headers=headers)
                response.raise_for_status()
            data = response.json()
                
            rankings = data.get("rankings", [])
            logger.info(f"API 응답에서 {len(rankings)}개 캐릭터 발견")
            
            characters = []
            for idx, item in enumerate(rankings, 1):
                if idx > limit:
                    break
                
                character_id = item.get("id")
                name = item.get("name")
                description = item.get("shortDescription")
                view_count = item.get("interactionCount", 0)
                thumbnail_url = item.get("imageUrl")
                
                # 작성자 정보
                creator = item.get("creator", {})
                author = creator.get("nickname")
                
                # 태그 처리
                tags = item.get("hashtags", [])
                
                # 캐릭터 URL 구성
                character_url = f"{self.BASE_URL}/ko/plots/{character_id}/profile"
                
                characters.append(CharacterData(
                    character_id=character_id,
                    rank=idx,
                    name=name,
                    author=author,
                    views=view_count,
                    tags=tags,
                    description=description,
                    thumbnail_url=thumbnail_url,
                    character_url=character_url
                ))
                
                logger.debug(f"#{idx} {name} - {view_count:,}회")
                
            logger.info(f"제타 크롤링 완료: {len(characters)}개 수집")
            return characters
            
        except Exception as e:
            logger.error(f"제타 API 크롤링 중 오류: {e}")
            return []


# 테스트용 코드
if __name__ == "__main__":
    async def test():
        logging.basicConfig(level=logging.DEBUG)
        crawler = ZetaCrawler()
        results = await crawler.crawl_rankings(10)
        print(f"\n=== 결과: {len(results)}개 ===")
        for char in results:
            print(f"#{char.rank} {char.name} - {char.views:,}회")
            if char.description:
                print(f"   설명: {char.description[:50]}...")
            if char.tags:
                print(f"   태그: {', '.join(char.tags[:3])}")
    
    asyncio.run(test())
