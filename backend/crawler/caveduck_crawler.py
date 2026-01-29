
import asyncio
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)

@dataclass
class CharacterData:
    character_id: str
    rank: int
    name: str
    author: Optional[str]
    views: int
    tags: Optional[List[str]]
    description: Optional[str]
    thumbnail_url: Optional[str]
    character_url: Optional[str]

class CaveduckCrawler:
    """
    Caveduck.io API Crawler
    Target API: https://caveduck.io/api/character/public
    """
    API_URL = "https://caveduck.io/api/character/public"
    BASE_URL = "https://caveduck.io"
    
    def __init__(self):
        self.timeout = 30.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://caveduck.io/',
            'Origin': 'https://caveduck.io'
        }

    def extract_hashtags(self, text: str) -> List[str]:
        if not text:
            return []
        import re
        # HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', ' ', str(text))
        # #해시태그 추출
        return re.findall(r'#([\w가-힣]+)', clean_text)

    async def fetch_character_detail(self, client: httpx.AsyncClient, uuid: str) -> dict:
        """캐릭터 상세 정보를 비동기로 가져옴"""
        try:
            url = f"{self.BASE_URL}/api/character/{uuid}"
            resp = await client.get(url, params={'locale': 'ko'})
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {}

    async def crawl_rankings(self, limit: int = 30) -> List[CharacterData]:
        logger.info(f"[{self.SERVICE_NAME if hasattr(self, 'SERVICE_NAME') else 'caveduck'}] Crawling started...")
        characters = []
        
        url = f"{self.BASE_URL}/api/character/public"
        params = {
            'includeAdminMainView': 'true',
            'numPerPage': limit,
            'page': 0,
            'showNsfw': 'false',
            'view': 'popular',
            'locale': 'ko'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': self.BASE_URL
        }
        
        try:
            async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                items = data.get('items', [])
                logger.info(f"Found {len(items)} items from list API")
                
                # 상세 정보 병렬 요청
                tasks = []
                valid_items = []
                
                for item in items:
                    uuid = item.get('uuid')
                    if uuid:
                        tasks.append(self.fetch_character_detail(client, uuid))
                        valid_items.append(item)
                
                details_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                seen_ids = set()
                rank = 1
                
                for item, detail_result in zip(valid_items, details_results):
                    try:
                        char_id = str(item.get('id') or item.get('uuid'))
                        if char_id in seen_ids:
                            continue
                            
                        details = item.get('details', {})
                        name = item.get('name') or details.get('char_name') or "Unknown"
                        
                        creator = item.get('creator', 'Unknown')
                        if isinstance(creator, dict):
                            author = creator.get('nickname')
                        elif isinstance(creator, str):
                            author = creator
                        else:
                            author = "Unknown"
                        
                        views = item.get('messages') or item.get('chats') or 0
                        
                        # --- tags ---
                        tags = []
                        if isinstance(detail_result, dict):
                            official_tags = detail_result.get('tags', [])
                            if official_tags:
                                tags.extend([str(t) for t in official_tags])
                        
                        texts_to_scan = [
                            details.get('user_desc'),
                            item.get('short_description'),
                            details.get('short_description'),
                            details.get('creator_comment')
                        ]
                        
                        for text in texts_to_scan:
                            found = self.extract_hashtags(text)
                            tags.extend(found)
                            
                        tags = sorted(list(set(tags)))
                        
                        description = item.get('short_description') or item.get('description') or details.get('short_description')
                        thumbnail_url = item.get('image') or item.get('profile_image_url')
                        
                        item_uuid = item.get('uuid')
                        character_url = f"{self.BASE_URL}/character-info/{item_uuid}" if item_uuid else f"{self.BASE_URL}/character-info/{char_id}"
                        
                        characters.append(CharacterData(
                            character_id=char_id,
                            rank=rank,
                            name=name,
                            author=author,
                            views=views,
                            tags=tags,
                            description=description,
                            thumbnail_url=thumbnail_url,
                            character_url=character_url
                        ))
                        seen_ids.add(char_id)
                        rank += 1
                        
                    except Exception as e:
                        logger.warning(f"Error parsing item {rank}: {e}")
                        continue
                        
                return characters

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return []
