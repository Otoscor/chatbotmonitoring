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
        """인기 캐릭터 순위 크롤링"""
        logger.info(f"제타 크롤링 시작 (상위 {limit}개)")
        
        html = await self._fetch_html(self.RANKING_URL)
        if not html:
            logger.error("HTML을 가져오지 못했습니다.")
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        characters = []
        
        # /ko/plots/{UUID}/profile 형식의 링크 찾기
        plot_links = soup.find_all('a', href=re.compile(r'/ko/plots/[^/]+/profile'))
        logger.info(f"발견된 캐릭터 링크: {len(plot_links)}개")
        
        # 중복 제거를 위해 이미 처리한 캐릭터 ID 추적
        seen_ids = set()
        rank = 1
        
        for link in plot_links:
            if rank > limit:
                break
            
            href = link.get('href', '')
            char_id = self._extract_character_id(href)
            
            # 중복 체크
            if char_id in seen_ids:
                continue
            
            try:
                text = link.get_text(strip=True)
                
                # 조회수 링크인지 확인 (숫자만 있는 텍스트)
                if not re.match(r'^[\d,\.]+[만천]?$', text):
                    continue
                
                views = self._parse_views(text)
                
                # 같은 href를 가진 다른 링크에서 이름 링크 찾기
                all_same_href = soup.find_all('a', href=href)
                name_link = None
                for l in all_same_href:
                    l_text = l.get_text(strip=True)
                    if l_text != text:  # 조회수가 아닌 링크
                        name_link = l
                        break
                
                if not name_link:
                    continue
                
                # 이름 링크에서 span 요소들 추출
                spans = name_link.find_all('span')
                if len(spans) < 2:
                    continue
                
                name = spans[0].get_text(strip=True)
                description = spans[1].get_text(strip=True) if len(spans) > 1 else None
                
                if not name:
                    continue
                
                # 태그 추출 (부모에서 찾기)
                tags = None
                parent = name_link.parent
                if parent:
                    # 부모 내의 모든 div를 검색하여 '#'로 시작하는 텍스트 찾기
                    all_divs = parent.find_all('div')
                    for div in all_divs:
                        div_text = div.get_text(strip=True)
                        if div_text and div_text.startswith('#'):
                            # '#'로 구분하여 태그 리스트 생성
                            tags = [t.strip() for t in div_text.split('#') if t.strip()]
                            break
                
                character_url = f"{self.BASE_URL}{href}"
                
                characters.append(CharacterData(
                    character_id=char_id,
                    rank=rank,
                    name=name,
                    author=None,
                    views=views,
                    tags=tags,
                    description=description,
                    thumbnail_url=None,
                    character_url=character_url
                ))
                
                seen_ids.add(char_id)
                rank += 1
                logger.debug(f"#{rank-1} {name} - {views:,}회")
            
            except Exception as e:
                logger.warning(f"캐릭터 파싱 중 오류: {e}")
                continue
        
        logger.info(f"제타 크롤링 완료: {len(characters)}개 수집")
        return characters


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
