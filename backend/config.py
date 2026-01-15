"""
애플리케이션 설정 관리
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Database
    # 프로덕션에서는 환경 변수 DATABASE_URL 사용 (PostgreSQL)
    # 로컬 개발에서는 SQLite 사용
    database_url: str = "sqlite+aiosqlite:///./monitoring.db"
    
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """캐시된 설정 인스턴스 반환"""
    return Settings()
