"""
애플리케이션 설정 관리
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Database
    # 프로덕션에서는 환경 변수 DATABASE_URL 사용 (PostgreSQL)
    # 로컬 개발에서는 SQLite 사용 (backend 디렉토리 기준 절대 경로)
    database_url: str = f"sqlite+aiosqlite:///{Path(__file__).parent}/monitoring.db"
    
    # Crawler Settings
    crawl_delay_seconds: float = 1.5
    max_pages_per_crawl: int = 3  # 테스트용으로 3페이지로 감소
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    
    # Target Galleries - 여러 갤러리 지원
    target_galleries: List[dict] = [
        {
            "id": "wrtnai",
            "name": "뤼튼 마이너갤",
            "type": "dcinside_minor",
            "url": "https://gall.dcinside.com/mgallery/board/lists/?id=wrtnai"
        },
        {
            "id": "aichatting",
            "name": "AI챗팅 마이너갤",
            "type": "dcinside_minor",
            "url": "https://gall.dcinside.com/mgallery/board/lists/?id=aichatting"
        },
        {
            "id": "characterai",
            "name": "아카라이브 캐릭터AI",
            "type": "arcalive",
            "url": "https://arca.live/b/characterai"
        }
    ]
    
    # 뉴스 검색 키워드 (구글 뉴스 RSS)
    news_keywords: List[str] = ["AI 챗봇", "AI 캐릭터", "뤼튼"]
    
    # 앱 리뷰 크롤링 대상
    target_apps: List[dict] = [
        {
            "name": "Character AI",
            "google_play_id": "ai.character.app",
            "app_store_id": "1547856149",
            "app_store_name": "character-ai",
            "country": "kr"
        },
        {
            "name": "제타 (Zeta)",
            "google_play_id": "com.scatterlab.messenger",
            "app_store_id": "6450491005",
            "app_store_name": "zeta-ai-chat-live-stories",
            "country": "kr"
        },
        {
            "name": "루나톡 (Lunatalk)",
            "google_play_id": "com.lunatalk.app",
            "app_store_id": "6473849158",
            "app_store_name": "lunatalk",
            "country": "kr"
        },
        {
            "name": "베이브챗 (Babechat)",
            "google_play_id": "ai.babechat.app",
            "app_store_id": "6479106254",
            "app_store_name": "babechat-ai-character-chat",
            "country": "kr"
        },
        {
            "name": "케이브덕 (Caveduck)",
            "google_play_id": "com.warpspace.caveduckaos",
            "app_store_id": "6504139571",
            "app_store_name": "caveduck",
            "country": "kr"
        },

        {
            "name": "러비더비 (LoveyDovey)",
            "google_play_id": "ai.tain.reelso",  # 실제 패키지명
            "app_store_id": None,
            "app_store_name": "loveydovey-dream-chats",
            "country": "kr"
        },
        {
            "name": "로판AI (Rofan AI)",
            "google_play_id": "ai.rofan.app",
            "app_store_id": None,  # 검색 필요
            "app_store_name": "rofan-ai",
            "country": "kr"
        },
        {
            "name": "팅글 (Tingle)",
            "google_play_id": "com.bubbletap.tinglechat",
            "app_store_id": None,  # 검색 필요
            "app_store_name": "tinglechat",
            "country": "kr"
        },
        {
            "name": "크랙 (Crack)",
            "google_play_id": "com.wrtn.character",
            "app_store_id": None,
            "app_store_name": "wrtn-character",
            "country": "kr"
        }
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """캐시된 설정 인스턴스 반환"""
    return Settings()
