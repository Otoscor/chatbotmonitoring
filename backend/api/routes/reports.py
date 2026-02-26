"""
리포트 API 라우트
"""
from collections import Counter
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, DailyReport, ChatServiceCharacter
from api.schemas.reports import DailyReportResponse
from api.utils.date_utils import get_day_boundaries, parse_date_string

router = APIRouter()


@router.get("/reports", response_model=List[DailyReportResponse])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """리포트 목록 조회"""
    query = select(DailyReport).order_by(desc(DailyReport.report_date)).offset(skip).limit(limit)
    result = await db.execute(query)
    reports = result.scalars().all()
    return reports


@router.get("/reports/latest", response_model=DailyReportResponse)
async def get_latest_report(db: AsyncSession = Depends(get_db)):
    """최신 리포트 조회"""
    query = select(DailyReport).order_by(desc(DailyReport.report_date)).limit(1)
    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="리포트가 없습니다")

    return report


@router.get("/reports/{date}", response_model=DailyReportResponse)
async def get_report_by_date(date: str, db: AsyncSession = Depends(get_db)):
    """특정 날짜 리포트 조회"""
    target_date = parse_date_string(date)
    if not target_date:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")

    start_of_day, end_of_day = get_day_boundaries(target_date)

    query = select(DailyReport).where(
        DailyReport.report_date >= start_of_day,
        DailyReport.report_date < end_of_day
    )
    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="해당 날짜의 리포트가 없습니다")

    return report


@router.get("/reports/{date}/keywords")
async def get_report_keywords(
    date: str,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """특정 날짜 리포트의 인기 키워드 조회"""
    target_date = parse_date_string(date)
    if not target_date:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")

    start_of_day, end_of_day = get_day_boundaries(target_date)

    query = select(DailyReport).where(
        DailyReport.report_date >= start_of_day,
        DailyReport.report_date < end_of_day
    )
    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report or not report.top_keywords:
        return []

    keywords = []
    for item in report.top_keywords[:limit]:
        if isinstance(item, dict):
            keywords.append({
                "text": item.get("keyword", ""),
                "value": item.get("count", 0)
            })

    return keywords


@router.get("/reports/{date}/characters")
async def get_report_characters(
    date: str,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """특정 날짜 리포트의 인기 캐릭터 조회"""
    target_date = parse_date_string(date)
    if not target_date:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")

    start_of_day, end_of_day = get_day_boundaries(target_date)

    query = select(DailyReport).where(
        DailyReport.report_date >= start_of_day,
        DailyReport.report_date < end_of_day
    )
    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report or not report.top_characters:
        return []

    return report.top_characters[:limit]


@router.get("/reports/{date}/tags")
async def get_report_tags(
    date: str,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """특정 날짜의 인기 해시태그 조회 (캐릭터챗 서비스)"""
    target_date = parse_date_string(date)
    if not target_date:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")

    start_of_day, end_of_day = get_day_boundaries(target_date)

    query = select(ChatServiceCharacter.tags).where(
        ChatServiceCharacter.crawled_at >= start_of_day,
        ChatServiceCharacter.crawled_at < end_of_day,
        ChatServiceCharacter.tags.isnot(None)
    )

    result = await db.execute(query)
    all_tags_lists = result.scalars().all()

    if not all_tags_lists:
        return []

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
