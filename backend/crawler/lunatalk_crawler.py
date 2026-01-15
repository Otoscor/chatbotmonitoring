"""
루나톡(LUNATALK) AI 캐릭터 크롤러

루나톡은 한국 AI 캐릭터 채팅 서비스로,
정적 HTML을 사용하여 일반 HTTP 요청으로 크롤링이 가능합니다.
"""
import asyncio
import re
from datetime import datetime
from typing import List, Optional
import logging

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from config import get_settings

logger = logging.getLogger(__name__)


class CharacterData:
    """캐릭터 데이터 클래스"""
    def __init__(self, character_id: str, rank: int, name: str, author: Optional[str],
                 views: int, tags: Optional[List[str]], description: Optional[str],
                 thumbnail_url: Optional[str], character_url: str):
        self.character_id = character_id
        self.rank = rank
        self.name = name
        self.author = author
        self.views = views
        self.tags = tags
        self.description = description
        self.thumbnail_url = thumbnail_url
        self.character_url = character_url


class LunaTalkCrawler:
    """루나톡 AI 크롤러"""
    BASE_URL = "https://lunatalk.chat"
    
    def __init__(self):
        self.settings = get_settings()
        self.ua = UserAgent()
        self.delay = self.settings.crawl_delay_seconds
        self.max_retries = 3
    
    async def _fetch_html(self, url: str) -> Optional[str]:
        """HTML 페이지 가져오기"""
        headers = {"User-Agent": self.ua.random}
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    response = await client.get(url, headers=headers, timeout=30.0)
                    response.raise_for_status()
                    await asyncio.sleep(self.delay)
                    return response.text
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 오류 {url}: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"요청 오류 {url}: {e}")
            except Exception as e:
                logger.error(f"예상치 못한 오류 {url}: {e}")
            
            logger.warning(f"재시도 중... ({attempt + 1}/{self.max_retries})")
            await asyncio.sleep(self.delay * (attempt + 1))
        
        return None
    
    def _parse_views(self, view_str: str) -> int:
        """조회수 문자열을 정수로 변환 (예: "598,508" -> 598508)"""
        try:
            view_str = view_str.replace(",", "").strip()
            return int(view_str)
        except (ValueError, AttributeError):
            return 0
    
    def _extract_character_id(self, href: str) -> str:
        """URL에서 캐릭터 ID 추출 (/character/detail/44501 -> 44501)"""
        match = re.search(r'/character/detail/(\d+)', href)
        return match.group(1) if match else ""
    
    async def crawl_rankings(self, limit: int = 30, period: str = "daily") -> List[CharacterData]:
        """
        인기 캐릭터 순위 크롤링
        
        Args:
            limit: 수집할 캐릭터 수 (기본 30)
            period: 순위 기간 ("daily", "weekly", "monthly", "new", "overall")
        
        Returns:
            캐릭터 데이터 리스트
        """
        logger.info(f"루나톡 크롤링 시작 (상위 {limit}개, {period} 랭킹)")
        
        # 기간별 URL 설정
        if period == "overall":
            url = f"{self.BASE_URL}/character/rank"
        else:
            url = f"{self.BASE_URL}/character/rank?period={period}"
        
        html = await self._fetch_html(url)
        
        if not html:
            logger.error("HTML을 가져오지 못했습니다.")
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        characters = []
        
        # 캐릭터 카드 찾기 (class="cCont")
        character_cards = soup.find_all('div', class_='cCont')
        logger.info(f"발견된 캐릭터 카드: {len(character_cards)}개")
        
        for idx, card in enumerate(character_cards[:limit], start=1):
            try:
                # 링크 및 ID 추출
                link = card.find('a', href=True)
                if not link:
                    continue
                
                href = link['href']
                char_id = self._extract_character_id(href)
                if not char_id:
                    continue
                
                # 순위 추출
                rank_tag = card.find('div', class_='rankTag')
                rank = int(rank_tag.get_text(strip=True)) if rank_tag else idx
                
                # 이름 추출
                title_elem = card.find('h5', class_='lTit')
                name = title_elem.get_text(strip=True) if title_elem else "제목 없음"
                
                # 설명 추출 (lTxt 내의 p 태그)
                desc_elem = card.find('div', class_='lTxt')
                description = None
                if desc_elem:
                    p_elem = desc_elem.find('p')
                    if p_elem:
                        description = p_elem.get_text(strip=True)
                
                # 태그 추출
                tags = []
                tag_ul = card.find('ul', class_='lTag')
                if tag_ul:
                    tag_items = tag_ul.find_all('li')
                    tags = [tag.get_text(strip=True) for tag in tag_items]
                
                # 조회수/채팅 수 추출
                views = 0
                chat_elem = card.find('div', class_='lChat')
                if chat_elem:
                    span = chat_elem.find('span')
                    if span:
                        views = self._parse_views(span.get_text(strip=True))
                
                # 썸네일 URL 추출
                thumbnail_url = None
                img = card.find('img')
                if img and img.get('src'):
                    thumbnail_url = img['src']
                    # 상대 경로를 절대 경로로 변환
                    if thumbnail_url.startswith('/'):
                        thumbnail_url = f"{self.BASE_URL}{thumbnail_url}"
                
                # 캐릭터 URL
                character_url = f"{self.BASE_URL}{href}"
                
                # 작성자 정보는 랭킹 페이지에서 제공하지 않음
                author = None
                
                characters.append(CharacterData(
                    character_id=char_id,
                    rank=rank,
                    name=name,
                    author=author,
                    views=views,
                    tags=tags if tags else None,
                    description=description,
                    thumbnail_url=thumbnail_url,
                    character_url=character_url
                ))
                
                logger.debug(f"#{rank} {name} - {views:,}회")
                
            except Exception as e:
                logger.error(f"루나톡 캐릭터 파싱 오류 (카드 {idx}): {e}")
                continue
        
        logger.info(f"루나톡 크롤링 완료: {len(characters)}개 수집")
        return characters


# 테스트용 코드
if __name__ == "__main__":
    async def test():
        logging.basicConfig(level=logging.INFO)
        crawler = LunaTalkCrawler()
        
        # 일간 랭킹 테스트
        results = await crawler.crawl_rankings(limit=10, period="daily")
        
        print(f"\n=== 루나톡 일간 랭킹 TOP 10 ===")
        for char in results:
            print(f"#{char.rank} {char.name}")
            print(f"  조회수: {char.views:,}")
            if char.tags:
                print(f"  태그: {', '.join(char.tags)}")
            if char.description:
                print(f"  설명: {char.description[:50]}...")
            print()
    
    asyncio.run(test())
