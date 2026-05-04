
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

class ElynCrawler:
    """
    Elyn.ai API Crawler
    Target API: https://api.oracle.elyn.ai/api/v1/recommendations
    """
    API_URL = "https://api.oracle.elyn.ai/api/v1/recommendations"
    BASE_URL = "https://elyn.ai"
    
    def __init__(self):
        self.timeout = 30.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://elyn.ai/',
            'Origin': 'https://elyn.ai'
        }

    async def crawl_rankings(self, limit: int = 30) -> List[CharacterData]:
        logger.info(f"엘린 API 크롤링 시작 (상위 {limit}개)")
        characters = []

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                # Elyn recommendations API includes 'trending' category
                params = {
                    'limit': max(limit, 50), # Fetch enough to filter
                    'target': 'all'
                }
                
                response = await client.get(self.API_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Parse categories to find 'trending' or just take the first list of characters
                items = []
                
                # Check structure
                if 'categories' in data:
                    for category in data['categories']:
                        if category.get('type') == 'trending':
                            logger.info("Found 'trending' category")
                            items = category.get('items', [])
                            break
                    
                    # Fallback to first category if trending not found
                    if not items and data['categories']:
                        logger.info("Trending category not found, using first category")
                        items = data['categories'][0].get('items', [])
                
                if not items:
                    logger.warning("No items found in Elyn API response")
                    return []

                logger.info(f"Found {len(items)} items from API")
                
                rank = 1
                seen_ids = set()

                for item in items:
                    if len(characters) >= limit:
                        break
                    
                    # Item structure check
                    # item: {id, name, creator: {nickname, ...}, profileImageUrl, ...}
                    try:
                        if not isinstance(item, dict):
                            logger.debug(f"Skipping non-dict item: {item}")
                            continue

                        char_id = item.get('id')
                        if not char_id or char_id in seen_ids:
                            continue

                        name = item.get('name', 'Unknown')
                        
                        # Author/Creator
                        author = None
                        creator = item.get('creator')
                        if isinstance(creator, dict):
                            author = creator.get('nickname')
                        
                        # Views/Chat count
                        # Elyn API might have 'chatCount' or 'score'
                        views = item.get('chatCount', 0)
                        if not views:
                            # Try other fields or string parsing if needed
                            # Some APIs return formatted strings, but usually JSON has numbers
                            views = item.get('reactionCount', 0) # Fallback

                        # Description
                        description = item.get('description') or item.get('introduction')
                        
                        # Tags
                        tags_data = item.get('tags', [])
                        tags = []
                        if isinstance(tags_data, list):
                            tags = []
                            for t in tags_data:
                                if isinstance(t, dict):
                                    tags.append(t.get('name', ''))
                                elif isinstance(t, str):
                                    tags.append(t)
                        
                        # Thumbnail
                        # Elyn provides profileImageUrl
                        thumbnail_url = item.get('profileImageUrl')
                        if not thumbnail_url:
                             thumbnail_url = item.get('imageUrl')

                        if thumbnail_url and not thumbnail_url.startswith('http'):
                             # Sometimes raw S3 keys or relative paths? 
                             # Elyn usually gives full URLs or cloudfront.
                             # If relative, prepend CDN if known, but safe to assume full URL
                             pass

                        character_url = f"{self.BASE_URL}/chat/{char_id}"
                        
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
                        logger.warning(f"Error parsing Elyn item: {e}")
                        continue

        except Exception as e:
            logger.error(f"Elyn API request failed: {e}")
            import traceback
            traceback.print_exc()

        logger.info(f"엘린 크롤링 완료: {len(characters)}개 수집")
        return characters
