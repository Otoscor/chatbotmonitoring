"""
베이비챗(BabeChat) AI 캐릭터 크롤러

BabeChat API를 사용하여 인기 캐릭터 데이터를 수집합니다.
API가 막힐 경우 Playwright 폴백을 사용합니다.
"""
import asyncio
from typing import List, Optional
from dataclasses import dataclass
import logging
import json

import httpx

logger = logging.getLogger(__name__)


@dataclass
class CharacterData:
    """캐릭터 데이터"""
    character_id: str
    rank: int
    name: str
    author: Optional[str]
    views: int  # chatCount를 views로 매핑
    tags: Optional[List[str]]
    description: Optional[str]
    thumbnail_url: Optional[str]
    character_url: Optional[str]


class BabeChatCrawler:
    """베이비챗 AI 크롤러"""
    BASE_URL = "https://babechat.ai"
    API_URL = "https://api.babechatapi.com"
    
    def __init__(self):
        self.max_retries = 3
        self.delay = 1.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://babechat.ai/ko",
            "Origin": "https://babechat.ai",
        }
    
    async def _fetch_api(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """API 호출"""
        url = f"{self.API_URL}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        url, 
                        headers=self.headers,
                        params=params
                    )
                    response.raise_for_status()
                    await asyncio.sleep(self.delay)
                    return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 오류 {url}: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"요청 오류 {url}: {e}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류 {url}: {e}")
            except Exception as e:
                logger.error(f"예상치 못한 오류 {url}: {e}")
            
            if attempt < self.max_retries - 1:
                logger.warning(f"재시도 중... ({attempt + 1}/{self.max_retries})")
                await asyncio.sleep(self.delay * (attempt + 1))
        
        return None
    
    async def crawl_rankings(self, limit: int = 30) -> List[CharacterData]:
        """인기 캐릭터 순위 크롤링 (API 방식)"""
        logger.info(f"베이비챗 크롤링 시작 (상위 {limit}개)")
        
        # API로 인기 캐릭터 조회
        data = await self._fetch_api(
            "/ko/api/characters",
            params={
                "limit": limit,
                "sort": "popular"
            }
        )
        
        if not data:
            logger.warning("API 응답이 없습니다. Playwright 폴백 시도...")
            return await self._crawl_with_playwright(limit)
        
        characters = []
        
        for i, char in enumerate(data, start=1):
            if i > limit:
                break
            
            try:
                character_id = char.get("id") or char.get("characterId", "")
                name = char.get("name", "")
                chat_count = char.get("chatCount", 0)
                author = char.get("creatorNickname")
                tags = char.get("tags", [])
                description = char.get("description", "")
                thumbnail_url = char.get("mainImage")
                
                # 캐릭터 URL 생성 (BabeChat은 로그인 필요하므로 메인 페이지로 연결)
                character_url = f"{self.BASE_URL}/ko/dashboard"
                
                characters.append(CharacterData(
                    character_id=character_id,
                    rank=i,
                    name=name,
                    author=author,
                    views=chat_count,  # chatCount를 views로 사용
                    tags=tags if tags else None,
                    description=description[:200] if description else None,
                    thumbnail_url=thumbnail_url,
                    character_url=character_url
                ))
                
                logger.debug(f"#{i} {name} - {chat_count:,}회 채팅")
                
            except Exception as e:
                logger.warning(f"캐릭터 파싱 중 오류: {e}")
                continue
        
        logger.info(f"베이비챗 크롤링 완료: {len(characters)}개 수집")
        return characters
    
    async def _crawl_with_playwright(self, limit: int = 30) -> List[CharacterData]:
        """Playwright를 사용한 폴백 크롤링"""
        logger.info("Playwright 폴백 크롤링 시작...")
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright가 설치되어 있지 않습니다.")
            return []
        
        characters = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # API 응답 캡처
                api_data = []
                
                async def handle_response(response):
                    if "/api/characters" in response.url and response.status == 200:
                        try:
                            data = await response.json()
                            if isinstance(data, list):
                                api_data.extend(data)
                        except:
                            pass
                
                page.on("response", handle_response)
                
                logger.info("베이비챗 페이지 로딩 중...")
                await page.goto(
                    f"{self.BASE_URL}/ko",
                    wait_until="load",
                    timeout=60000
                )
                
                # JavaScript 로딩 대기
                await asyncio.sleep(10)
                
                # 스크롤하여 더 많은 데이터 로드
                for _ in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                
                await browser.close()
                
                # 수집된 API 데이터 처리
                seen_ids = set()
                rank = 1
                
                # chatCount 기준으로 정렬
                api_data.sort(key=lambda x: x.get("chatCount", 0), reverse=True)
                
                for char in api_data:
                    if rank > limit:
                        break
                    
                    char_id = char.get("id") or char.get("characterId", "")
                    if char_id in seen_ids:
                        continue
                    
                    seen_ids.add(char_id)
                    
                    characters.append(CharacterData(
                        character_id=char_id,
                        rank=rank,
                        name=char.get("name", ""),
                        author=char.get("creatorNickname"),
                        views=char.get("chatCount", 0),
                        tags=char.get("tags"),
                        description=char.get("description", "")[:200] if char.get("description") else None,
                        thumbnail_url=char.get("mainImage"),
                        character_url=f"{self.BASE_URL}/ko/dashboard"
                    ))
                    
                    rank += 1
                
                logger.info(f"Playwright 크롤링 완료: {len(characters)}개 수집")
                
        except Exception as e:
            logger.error(f"Playwright 크롤링 실패: {e}")
        
        return characters
    
    async def crawl_by_category(self, category: str = "all", limit: int = 30) -> List[CharacterData]:
        """카테고리별 캐릭터 크롤링
        
        Args:
            category: 카테고리 (all, male, female)
            limit: 수집할 캐릭터 수
        """
        logger.info(f"베이비챗 카테고리({category}) 크롤링 시작")
        
        params = {
            "limit": limit,
            "sort": "popular"
        }
        
        if category in ["male", "female"]:
            params["targetGender"] = category
        
        data = await self._fetch_api("/ko/api/characters", params=params)
        
        if not data:
            logger.warning("API 응답이 없습니다.")
            return []
        
        characters = []
        
        for i, char in enumerate(data, start=1):
            if i > limit:
                break
            
            try:
                character_id = char.get("id") or char.get("characterId", "")
                
                characters.append(CharacterData(
                    character_id=character_id,
                    rank=i,
                    name=char.get("name", ""),
                    author=char.get("creatorNickname"),
                    views=char.get("chatCount", 0),
                    tags=char.get("tags"),
                    description=char.get("description", "")[:200] if char.get("description") else None,
                    thumbnail_url=char.get("mainImage"),
                    character_url=f"{self.BASE_URL}/ko/dashboard"
                ))
            except Exception as e:
                logger.warning(f"캐릭터 파싱 중 오류: {e}")
                continue
        
        logger.info(f"카테고리({category}) 크롤링 완료: {len(characters)}개")
        return characters


# 테스트용 코드
if __name__ == "__main__":
    async def test():
        logging.basicConfig(level=logging.DEBUG)
        crawler = BabeChatCrawler()
        
        print("\n" + "="*70)
        print("베이비챗 인기 캐릭터 크롤링 테스트")
        print("="*70)
        
        results = await crawler.crawl_rankings(10)
        
        print(f"\n=== 결과: {len(results)}개 ===")
        for char in results:
            print(f"#{char.rank} {char.name}")
            print(f"   채팅수: {char.views:,}회")
            print(f"   작성자: {char.author}")
            if char.tags:
                print(f"   태그: {', '.join(char.tags[:3])}")
            if char.description:
                print(f"   설명: {char.description[:50]}...")
            print()
    
    asyncio.run(test())
