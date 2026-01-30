
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
    
    TAG_TRANSLATIONS = {
        "Academy": "아카데미",
        "Action": "액션",
        "Adventure": "모험",
        "Adult": "성인",
        "Aliens": "외계인",
        "Androids": "안드로이드",
        "Angst": "앵스트",
        "Animals": "동물",
        "Anime": "애니메이션",
        "Anthropomorphic": "의인화",
        "Apocalypse": "아포칼립스",
        "Arranged Marriage": "정략결혼",
        "Artist": "예술가",
        "Assassin": "암살자",
        "Assistant": "조수",
        "Ayandere": "아얀데레",
        "Baby": "아기",
        "Bad Ending": "배드 엔딩",
        "BDSM": "BDSM",
        "Beach": "해변",
        "Beastkin": "수인",
        "Beauty": "미녀",
        "Best Friend": "가장 친한 친구",
        "Biblical": "성경",
        "Biker": "바이커",
        "Blackmail": "협박",
        "Blind": "맹인",
        "Bodyguard": "경호원",
        "Book": "책",
        "Boss": "보스",
        "Boyfriend": "남친",
        "Boys Love": "BL",
        "Bully": "일진",
        "Butler": "집사",
        "Celebrity": "연예인",
        "Cheating": "바람",
        "Childhood Friend": "소꿉친구",
        "Chuunibyou": "중2병",
        "Comedy": "코미디",
        "Contemporary": "현대",
        "Contemporary fantasy": "현대 판타지",
        "Cowboy": "카우보이",
        "Creepy": "공포",
        "Crime": "범죄",
        "Crossdressing": "여장",
        "Cult": "사이비",
        "Cyberpunk": "사이버펑크",
        "Dandere": "단데레",
        "Dark": "다크",
        "Dark Fantasy": "다크 판타지",
        "Dead Dove": "피폐",
        "Demon": "악마",
        "Demon Lord": "마왕",
        "Detective": "탐정",
        "Devil": "악마",
        "Dilf": "중년남",
        "Dinosaur": "공룡",
        "Discord Mod": "디스코드 관리자",
        "Doctor": "의사",
        "Dominant": "지배적인",
        "Drama": "드라마",
        "Dragon": "드래곤",
        "Drug Dealer": "마약상",
        "Dystopian": "디스토피아",
        "Elf": "엘프",
        "Enemy": "적",
        "Enemies to Lovers": "혐관",
        "Ex-Boyfriend": "전남친",
        "Ex-Girlfriend": "전여친",
        "Experimental": "실험적인",
        "Fantasy": "판타지",
        "Family": "가족",
        "family": "가족",
        "Famous": "유명인",
        "Femboy": "오토코노코",
        "Female": "여성",
        "Fictional Character": "가상의 캐릭터",
        "Firefighter": "소방관",
        "Flirting": "플러팅",
        "Friends": "친구",
        "Friends to Lovers": "친구에서 연인으로",
        "Furry": "퍼리",
        "Futuristic": "미래",
        "Game Character": "게임 캐릭터",
        "Gamer": "게이머",
        "Gang": "갱단",
        "Games": "게임",
        "Gender Bender": "성전환",
        "Gentle Male": "다정남",
        "Ghost": "유령",
        "Giant": "거인",
        "Girlfriend": "여친",
        "Girls Love": "GL",
        "God": "신",
        "Goth": "고스",
        "Harem": "하렘",
        "Hero": "영웅",
        "High School": "고등학교",
        "Historical": "시대물",
        "History": "역사",
        "Homeless": "노숙자",
        "Horror": "공포",
        "Human": "인간",
        "Idol": "아이돌",
        "Incest": "근친",
        "Isekai": "이세계",
        "Josei": "여성향",
        "K-Pop": "K-Pop",
        "Kidnapping": "납치",
        "Knight": "기사",
        "Kuudere": "쿨데레",
        "Living Together": "동거",
        "Love": "사랑",
        "Love-Hate": "애증",
        "Love Triangle": "삼각관계",
        "Lovers": "연인",
        "Mafia": "마피아",
        "Magic": "마법",
        "Maid": "메이드",
        "male": "남성",
        "Manhwa": "만화",
        "Marriage": "결혼",
        "Married": "기혼",
        "Master": "주인님",
        "Medieval": "중세",
        "Mermaid": "인어",
        "Military": "군인",
        "Milf": "밀프",
        "Mind Control": "최면",
        "Minecraft": "마인크래프트",
        "Monster": "몬스터",
        "Monster Girl": "몬스터걸",
        "Movie": "영화",
        "Multiple": "다인",
        "Murderer": "살인마",
        "Music": "음악",
        "Mystery": "미스터리",
        "Mythology": "신화",
        "Neighbor": "이웃",
        "Ninja": "닌자",
        "Non-Binary": "논바이너리",
        "Non-Human": "비인간",
        "Novel": "소설",
        "Nurse": "간호사",
        "Office": "오피스",
        "Older": "연상",
        "Omegaverse": "오메가버스",
        "One Piece": "원피스",
        "Orc": "오크",
        "original-character": "자작 캐릭터",
        "Otome": "오토메",
        "Parody": "패러디",
        "Pirate": "해적",
        "Playboy": "플레이보이",
        "Police": "경찰",
        "Politics": "정치",
        "Post-Apocalyptic": "포스트 아포칼립스",
        "Prison": "감옥",
        "Psychopath": "사이코패스",
        "Queen": "여왕",
        "Reality": "현실",
        "Relationship": "관계",
        "Religion": "종교",
        "Reverse Harem": "역하렘",
        "Rich": "부자",
        "Robot": "로봇",
        "Roleplay": "롤플레이",
        "Romance": "로맨스",
        "Roommate": "룸메이트",
        "Royal": "왕족",
        "RPG": "RPG",
        "Sad": "슬픔",
        "Samurai": "사무라이",
        "School": "학교",
        "School Life": "학교 생활",
        "Sci-Fi": "SF",
        "Scientist": "과학자",
        "Secretary": "비서",
        "Senpai": "선배",
        "Serial Killer": "연쇄살인마",
        "Slave": "노예",
        "Slice of Life": "일상",
        "Sly Male": "능글남",
        "Soldier": "군인",
        "Space": "우주",
        "Sports": "스포츠",
        "Spy": "스파이",
        "Star Wars": "스타워즈",
        "Steampunk": "스팀펑크",
        "Step-Sibling": "의붓형제",
        "Strategy": "전략",
        "Streamer": "스트리머",
        "Student": "학생",
        "Superhero": "슈퍼히어로",
        "Supernatural": "초자연",
        "Survival": "생존",
        "Sword and Magic": "검과 마법",
        "Teacher": "선생님",
        "Teenager": "십대",
        "Theory": "이론",
        "Thriller": "스릴러",
        "Time Travel": "시간여행",
        "Toxic": "유해한",
        "Trans": "트랜스",
        "Tsundere": "츤데레",
        "Twin": "쌍둥이",
        "Unrequited Love": "짝사랑",
        "Vampire": "뱀파이어",
        "Vanilla(pure love)": "순애",
        "Villain": "빌런",
        "Villainess": "악녀",
        "Virtual Reality": "가상현실",
        "Visual Novel": "비주얼 노벨",
        "Vtuber": "버튜버",
        "War": "전쟁",
        "Warrior": "전사",
        "Webtoon": "웹툰",
        "Western": "서부",
        "Witch": "마녀",
        "Wolf": "늑대",
        "Yandere": "얀데레",
        "YouTuber": "유튜버",
        "Zombie": "좀비",
        "blunt": "무뚝뚝",
        "female": "여성",
        "male": "남성",
        "modern": "현대",
        "Regret": "후회",
        "Simulator": "시뮬레이터"

    }
    
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
                                # 태그 번역 적용
                                translated_official_tags = []
                                for t in official_tags:
                                    tag_str = str(t)
                                    translated_official_tags.append(self.TAG_TRANSLATIONS.get(tag_str, tag_str))
                                tags.extend(translated_official_tags)
                        
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
