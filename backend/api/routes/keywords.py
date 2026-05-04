"""
키워드 및 캐릭터 랭킹 API 라우트
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, DailyReport

router = APIRouter()


@router.get("/keywords/trending")
async def get_trending_keywords(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """트렌딩 키워드 조회"""
    since = datetime.now() - timedelta(days=days)

    query = select(DailyReport).where(
        DailyReport.report_date >= since
    ).order_by(desc(DailyReport.report_date))

    result = await db.execute(query)
    reports = result.scalars().all()

    # 키워드 집계
    keyword_counts = {}
    for report in reports:
        if report.top_keywords:
            for kw in report.top_keywords:
                keyword = kw.get("keyword", "")
                count = kw.get("count", 0)
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + count

    # 정렬 및 상위 N개
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    return [{"keyword": k, "total_count": c, "rank": i+1} for i, (k, c) in enumerate(sorted_keywords)]


@router.get("/characters/ranking")
async def get_character_ranking(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """캐릭터 랭킹 조회"""
    since = datetime.now() - timedelta(days=days)

    query = select(DailyReport).where(
        DailyReport.report_date >= since
    ).order_by(desc(DailyReport.report_date))

    result = await db.execute(query)
    reports = result.scalars().all()

    # 캐릭터 언급 집계
    character_mentions = {}
    for report in reports:
        if report.top_characters:
            for char in report.top_characters:
                name = char.get("name", "")
                mentions = char.get("mentions", 0)
                character_mentions[name] = character_mentions.get(name, 0) + mentions

    # 정렬 및 상위 N개
    sorted_characters = sorted(character_mentions.items(), key=lambda x: x[1], reverse=True)[:limit]

    return [{"name": name, "total_mentions": mentions, "rank": i+1} for i, (name, mentions) in enumerate(sorted_characters)]
