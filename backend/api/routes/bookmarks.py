"""
북마크 API 라우트
"""
import asyncio
from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, AsyncSessionLocal, Bookmark
from api.schemas.bookmarks import BookmarkCreate, BookmarkUpdate, BookmarkResponse

logger = logging.getLogger(__name__)

router = APIRouter()


async def process_bookmark_background(bookmark_id: int, url: str):
    """백그라운드에서 메타데이터 추출 및 AI 요약 수행"""
    from utils.url_parser import extract_url_metadata

    async with AsyncSessionLocal() as session:
        try:
            # 1. 메타데이터 추출
            metadata = await extract_url_metadata(url)

            # DB 업데이트
            result = await session.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
            bookmark = result.scalar_one_or_none()

            if bookmark:
                if metadata.get('title'):
                    bookmark.title = metadata.get('title')
                if metadata.get('description'):
                    bookmark.description = metadata.get('description')
                if metadata.get('thumbnail'):
                    bookmark.thumbnail_url = metadata.get('thumbnail')
                if metadata.get('site_name'):
                    bookmark.site_name = metadata.get('site_name')

                await session.commit()

            # 다시 조회 (커밋 후 상태)
            if bookmark:
                bookmark.is_summarized = 1  # 요약 없이 완료 처리
                await session.commit()

        except Exception as e:
            logger.error(f"Error processing bookmark {bookmark_id}: {e}")
            try:
                result = await session.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
                bookmark = result.scalar_one_or_none()
                if bookmark:
                    bookmark.is_summarized = 2
                    await session.commit()
            except Exception as db_err:
                logger.error(f"Failed to update error status: {db_err}")


@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark: BookmarkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    북마크 추가

    URL을 즉시 저장하고, 메타데이터 추출 및 AI 요약은 백그라운드에서 처리합니다.
    """
    # 1. 북마크 즉시 생성 (기본 정보만)
    new_bookmark = Bookmark(
        url=bookmark.url,
        category=bookmark.category,
        title=bookmark.url,  # 임시 제목 (URL)
        is_summarized=0
    )

    db.add(new_bookmark)
    await db.commit()
    await db.refresh(new_bookmark)

    # 2. 백그라운드 작업 시작 (메타데이터 + 요약)
    asyncio.create_task(process_bookmark_background(new_bookmark.id, bookmark.url))

    return new_bookmark


@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def get_bookmarks(
    category: Optional[str] = Query(None, description="카테고리 필터 (post, news, creation)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """북마크 목록 조회 (최신순)"""
    query = select(Bookmark).order_by(desc(Bookmark.created_at))

    if category:
        query = query.where(Bookmark.category == category)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    bookmarks = result.scalars().all()
    return bookmarks


@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db)
):
    """북마크 상세 조회"""
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다")

    return bookmark


@router.put("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    update_data: BookmarkUpdate,
    db: AsyncSession = Depends(get_db)
):
    """북마크 수정 (태그, 메모)"""
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다")

    if update_data.tags is not None:
        bookmark.tags = update_data.tags
    if update_data.user_note is not None:
        bookmark.user_note = update_data.user_note

    await db.commit()
    await db.refresh(bookmark)

    return bookmark


@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db)
):
    """북마크 삭제"""
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다")

    await db.delete(bookmark)
    await db.commit()

    return {"message": "북마크가 삭제되었습니다"}


@router.post("/bookmarks/{bookmark_id}/summarize", response_model=BookmarkResponse)
async def resummarize_bookmark(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db)
):
    """AI 요약 재생성 (기능 제거됨)"""
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()

    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다")

    return bookmark
