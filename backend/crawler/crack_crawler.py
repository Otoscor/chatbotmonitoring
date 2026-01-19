import asyncio
from typing import List, Optional
from dataclasses import dataclass
import logging
import httpx
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)


@dataclass
class CharacterData:
    character_id: str
    rank: int
    name: str
    author: Optional[str]
    views: int  # totalMessageCount 사용
    tags: Optional[List[str]]
    description: Optional[str]
    thumbnail_url: Optional[str]
    character_url: Optional[str]


class CrackCrawler:
    BASE_URL = "https://crack.wrtn.ai"
    
    def __init__(self):
        self.delay = 0.5
        self.max_retries = 3

    async def crawl_rankings(self, limit: int = 30) -> List[CharacterData]:
        """
        Crack 메인 페이지에서 인기 캐릭터 크롤링
        - "떠오르는 신예 창작자들" 섹션
        - "공식 크리에이터들의 뜨거운 신작" 섹션
        """
        logger.info(f"크랙 크롤링 시작 (상위 {limit}개)")
        characters_data = []
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Referer': 'https://crack.wrtn.ai/'
                    }
                    
                    # 메인 페이지 HTML 가져오기
                    logger.info("메인 페이지 HTML 가져오는 중...")
                    response = await client.get(f"{self.BASE_URL}/", headers=headers)
                    response.raise_for_status()
                    
                    # BeautifulSoup으로 파싱
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # __NEXT_DATA__ 스크립트 찾기
                    next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
                    if not next_data_script:
                        logger.error("__NEXT_DATA__ 스크립트를 찾을 수 없습니다")
                        continue
                    
                    # JSON 파싱
                    next_data = json.loads(next_data_script.string)
                    
                    # buildId 추출
                    build_id = next_data.get('buildId')
                    logger.info(f"Build ID: {build_id}")
                    
                    # _next/data를 통해 JSON 데이터 직접 가져오기
                    json_url = f"{self.BASE_URL}/_next/data/{build_id}/index.json"
                    logger.info(f"JSON 데이터 가져오는 중: {json_url}")
                    
                    json_response = await client.get(json_url, headers=headers)
                    json_response.raise_for_status()
                    json_data = json_response.json()
                    
                    page_props = json_data.get('pageProps', {})
                    fallback = page_props.get('fallback', {})
                    
                    # 스토리 페이지 데이터 찾기
                    story_page_key = None
                    for key in fallback.keys():
                        if 'pages' in key and 'home=story' in key:
                            story_page_key = key
                            break
                    
                    if not story_page_key:
                        logger.error(f"스토리 페이지 데이터를 찾을 수 없습니다. Fallback 키: {list(fallback.keys())}")
                        continue
                    
                    # 섹션 데이터 추출
                    sections = fallback[story_page_key].get('data', {}).get('sections', [])
                    
                    # 캐릭터 섹션 찾기
                    # Section 4: "떠오르는 신예 창작자들"
                    # Section 5: "공식 크리에이터들의 뜨거운 신작"
                    all_characters = []
                    
                    for section in sections:
                        section_type = section.get('type')
                        section_title = section.get('title', '')
                        
                        # CharacterCarousel 타입 섹션만 처리
                        if section_type == 'CharacterCarousel':
                            items = section.get('items', [])
                            logger.info(f"섹션 '{section_title}' 발견: {len(items)}개 캐릭터")
                            all_characters.extend(items)
                    
                    if not all_characters:
                        logger.warning("캐릭터 데이터를 찾을 수 없습니다")
                        return []
                    
                    # totalMessageCount 기준으로 정렬 (내림차순)
                    all_characters.sort(
                        key=lambda x: x.get('totalMessageCount', 0),
                        reverse=True
                    )
                    
                    # 상위 limit개만 추출
                    for rank, char in enumerate(all_characters[:limit], 1):
                        character_id = char.get('_id')
                        name = char.get('name')
                        total_msg_count = char.get('totalMessageCount', 0)
                        
                        # 작가 정보
                        creator = char.get('creator', {})
                        author = None
                        if isinstance(creator, dict):
                            author = creator.get('nickname')
                        
                        # 태그
                        tags = char.get('tags', [])
                        
                        # 설명
                        description = char.get('description')
                        
                        # 썸네일 (imageUrl 또는 profileImageUrl)
                        thumbnail_url = char.get('imageUrl') or char.get('profileImageUrl')
                        
                        # 캐릭터 URL - 개별 페이지가 없으므로 캐릭터 목록 페이지로 연결
                        character_url = f"{self.BASE_URL}/characters"
                        
                        characters_data.append(CharacterData(
                            character_id=character_id,
                            rank=rank,
                            name=name,
                            author=author,
                            views=total_msg_count,
                            tags=tags,
                            description=description,
                            thumbnail_url=thumbnail_url,
                            character_url=character_url
                        ))
                        
                        logger.debug(f"#{rank} {name} - {total_msg_count:,}회 대화")
                    
                    break  # 성공 시 재시도 루프 탈출
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP 오류 {self.BASE_URL}: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"요청 오류 {self.BASE_URL}: {e}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {e}")
            except Exception as e:
                logger.error(f"예상치 못한 오류 {self.BASE_URL}: {e}")
                import traceback
                traceback.print_exc()
            
            if attempt < self.max_retries - 1:
                logger.warning(f"재시도 중... ({attempt + 1}/{self.max_retries})")
                await asyncio.sleep(self.delay * (attempt + 1))
        
        logger.info(f"크랙 크롤링 완료: {len(characters_data)}개 수집")
        return characters_data
