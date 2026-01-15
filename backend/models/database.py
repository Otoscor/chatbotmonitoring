"""
데이터베이스 모델 및 연결 관리
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON, Index, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from contextlib import asynccontextmanager

from config import get_settings

Base = declarative_base()


class Post(Base):
    """게시글 모델"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(50), unique=True, nullable=False, index=True)  # 원본 게시글 ID
    gallery_id = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=True)  # 게시글 작성 시간
    crawled_at = Column(DateTime, default=datetime.utcnow)  # 크롤링 시간
    view_count = Column(Integer, default=0)
    recommend_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    url = Column(String(500), nullable=True)
    
    # 관계
    keywords = relationship("PostKeyword", back_populates="post", cascade="all, delete-orphan")


class PostKeyword(Base):
    """게시글 키워드 모델"""
    __tablename__ = "post_keywords"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    keyword = Column(String(100), nullable=False, index=True)
    score = Column(Float, default=0.0)  # TF-IDF 점수 또는 빈도
    
    post = relationship("Post", back_populates="keywords")


class DailyReport(Base):
    """일일 리포트 모델"""
    __tablename__ = "daily_reports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(DateTime, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 통계
    total_posts = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_recommends = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    
    # 분석 결과 (JSON으로 저장)
    top_keywords = Column(JSON, nullable=True)  # [{"keyword": "xxx", "count": 10}, ...]
    top_characters = Column(JSON, nullable=True)  # [{"name": "xxx", "mentions": 10}, ...]
    sentiment_summary = Column(JSON, nullable=True)  # {"positive": 0.6, "negative": 0.2, "neutral": 0.2}
    trending_topics = Column(JSON, nullable=True)  # [{"topic": "xxx", "growth": 0.5}, ...]


class CharacterMention(Base):
    """캐릭터 언급 모델"""
    __tablename__ = "character_mentions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_name = Column(String(200), nullable=False, index=True)
    mention_date = Column(DateTime, nullable=False, index=True)
    mention_count = Column(Integer, default=1)
    source_gallery = Column(String(50), nullable=True)


class ChatServiceCharacter(Base):
    """캐릭터챗 서비스 캐릭터 모델"""
    __tablename__ = "chat_service_characters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String(50), nullable=False, index=True)  # 'zeta', 'babechat', 'crack', 'elyn'
    character_id = Column(String(100), nullable=False)  # 서비스 내 고유 ID
    rank = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    author = Column(String(200), nullable=True)
    views = Column(Integer, default=0)  # 조회수 (만 단위는 변환하여 저장)
    tags = Column(JSON, nullable=True)  # ["태그1", "태그2"]
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    character_url = Column(String(500), nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_service_rank', 'service', 'rank'),
    )


# 데이터베이스 엔진 및 세션
settings = get_settings()
async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """데이터베이스 초기화 - 테이블 생성"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_db_session():
    """데이터베이스 세션 컨텍스트 매니저"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db():
    """FastAPI 의존성 주입용 세션 생성기"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
