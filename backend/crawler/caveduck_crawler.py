
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

    async def crawl_rankings(self, limit: int = 30) -> List[CharacterData]:
        logger.info(f"케이브덕 API 크롤링 시작 (상위 {limit}개)")
        characters = []

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                params = {
                    'includeAdminMainView': 'true',
                    'numPerPage': max(limit, 40),
                    'page': 0,
                    'showNsfw': 'false',
                    'view': 'popular', # 'recent', 'popular' works. 'daily' failed in test. 'popular' seems best for ranking.
                    'locale': 'ko'
                }
                
                response = await client.get(self.API_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Check for 'items' list
                items = data.get('items', [])
                if not items:
                    logger.warning("No items found in Caveduck API response")
                    return []
                
                logger.info(f"Found {len(items)} items from API")

                rank = 1
                seen_ids = set()

                for item in items:
                    if len(characters) >= limit:
                        break

                    try:
                        # item structure: {id, name, creator: {nickname}, profile_image_url, ...}
                        # Need to inspect fields carefully. Assuming standard naming.
                        
                        # Use id (int) or uuid
                        # API returns integer id
                        char_id = str(item.get('id'))
                        if not char_id or char_id == 'None':
                            char_id = item.get('uuid')
                            
                        if not char_id or char_id in seen_ids:
                             continue

                        name = item.get('name', 'Unknown')
                        
                        # Author
                        author = None
                        creator = item.get('creator')
                        if isinstance(creator, dict):
                            author = creator.get('nickname')
                        elif isinstance(creator, str):
                            author = creator
                        
                        # Views / Usage
                        # Use messages or chats
                        views = item.get('messages') or item.get('chats') or 0
                        
                        # Tags
                        tags_data = item.get('tags', [])
                        tags = []
                        if isinstance(tags_data, list):
                            tags = [str(t) for t in tags_data]
                        
                        # Description
                        description = item.get('short_description') or item.get('description')

                        # Thumbnail matches
                        # Caveduck images are usually on cdn.caveduck.io
                        # 'image' field contains URL
                        thumbnail_url = item.get('image') or item.get('profile_image_url')
                        
                        # Character URL
                        # /shop/item/{id}
                        character_url = f"{self.BASE_URL}/shop/item/{char_id}"
                        
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
                        logger.warning(f"Error parsing Caveduck item: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Caveduck API request failed: {e}")
            import traceback
            traceback.print_exc()

        logger.info(f"케이브덕 크롤링 완료: {len(characters)}개 수집")
        return characters
