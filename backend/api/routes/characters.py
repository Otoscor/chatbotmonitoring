"""
캐릭터 챗봇 서비스 API 라우트
"""
from collections import Counter
from datetime import timedelta
from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, ChatServiceCharacter
from api.schemas.characters import ChatServiceCharacterResponse, CrawlChatServicesRequest
from crawler.character_service_crawler import crawl_all_character_services

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/characters/chat-services", response_model=List[ChatServiceCharacterResponse])
async def get_chat_service_characters(
    service: Optional[str] = Query(None, description="서비스 필터 (zeta, lunatalk, babechat, crack)"),
    limit: int = Query(30, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """캐릭터챗 서비스 순위 조회 (최신 크롤링 데이터)"""
    # 가장 최근 크롤링 시간 조회
    recent_crawl_query = select(func.max(ChatServiceCharacter.crawled_at))
    if service:
        recent_crawl_query = recent_crawl_query.where(ChatServiceCharacter.service == service)

    result = await db.execute(recent_crawl_query)
    recent_crawl_time = result.scalar()

    if not recent_crawl_time:
        return []

    # 최근 크롤링 시간 기준 5분 이내의 데이터 조회
    time_threshold = recent_crawl_time - timedelta(minutes=5)

    query = select(ChatServiceCharacter).where(
        ChatServiceCharacter.crawled_at >= time_threshold,
        ChatServiceCharacter.crawled_at <= recent_crawl_time
    )

    if service:
        query = query.where(ChatServiceCharacter.service == service)

    query = query.order_by(
        ChatServiceCharacter.rank,
        ChatServiceCharacter.service
    ).limit(limit)

    result = await db.execute(query)
    characters = result.scalars().all()

    return characters


@router.post("/characters/crawl-chat-services")
async def crawl_chat_services(
    request: CrawlChatServicesRequest,
    db: AsyncSession = Depends(get_db)
):
    """캐릭터챗 서비스 크롤링 트리거"""
    services = request.services
    try:
        # 크롤링 실행
        results = await crawl_all_character_services(services)

        # 기존 데이터 삭제 (선택된 서비스만)
        services_to_delete = services if services else ['zeta', 'babechat', 'lunatalk']
        for service in services_to_delete:
            await db.execute(
                select(ChatServiceCharacter).where(ChatServiceCharacter.service == service)
            )
            delete_query = ChatServiceCharacter.__table__.delete().where(
                ChatServiceCharacter.service == service
            )
            await db.execute(delete_query)

        # 새 데이터 저장
        saved_count = 0
        for service_name, characters in results.items():
            for char_data in characters:
                character = ChatServiceCharacter(
                    service=service_name,
                    character_id=char_data.character_id,
                    rank=char_data.rank,
                    name=char_data.name,
                    author=char_data.author,
                    views=char_data.views,
                    tags=char_data.tags,
                    description=char_data.description,
                    thumbnail_url=char_data.thumbnail_url,
                    character_url=char_data.character_url
                )
                db.add(character)
                saved_count += 1

        await db.commit()

        total_crawled = sum(len(chars) for chars in results.values())

        return {
            "success": True,
            "message": f"크롤링 완료: {total_crawled}개 수집, {saved_count}개 저장",
            "results": {
                service: len(chars) for service, chars in results.items()
            }
        }
    except Exception as e:
        logger.error(f"캐릭터 서비스 크롤링 실패: {e}")
        return {
            "success": False,
            "message": f"크롤링 실패: {str(e)}",
            "results": {}
        }


@router.get("/characters/popular-tags")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=50),
    service: Optional[str] = Query(None, description="서비스 필터 (zeta, lunatalk)"),
    db: AsyncSession = Depends(get_db)
):
    """
    인기 해시태그 조회
    캐릭터들의 태그를 집계하여 가장 많이 사용된 태그 반환
    """
    # 최근 크롤링 데이터 시간 확인
    recent_crawl_query = select(func.max(ChatServiceCharacter.crawled_at))
    if service:
        recent_crawl_query = recent_crawl_query.where(ChatServiceCharacter.service == service)

    result = await db.execute(recent_crawl_query)
    recent_crawl_time = result.scalar()

    if not recent_crawl_time:
        return []

    # 최근 5분 이내의 데이터 조회
    time_threshold = recent_crawl_time - timedelta(minutes=5)

    query = select(ChatServiceCharacter.tags).where(
        ChatServiceCharacter.crawled_at >= time_threshold,
        ChatServiceCharacter.crawled_at <= recent_crawl_time,
        ChatServiceCharacter.tags.isnot(None)
    )

    if service:
        query = query.where(ChatServiceCharacter.service == service)

    result = await db.execute(query)
    all_tags_lists = result.scalars().all()

    # 모든 태그를 평탄화하고 카운트
    tag_counter = Counter()

    for tags_list in all_tags_lists:
        if tags_list and isinstance(tags_list, list):
            tag_counter.update(tags_list)

    # 가장 많이 사용된 태그 반환
    popular_tags = [
        {"tag": tag, "count": count}
        for tag, count in tag_counter.most_common(limit)
    ]

    return popular_tags
