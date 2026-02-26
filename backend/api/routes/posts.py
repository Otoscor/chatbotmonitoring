"""
게시글 API 라우트
"""
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, Post
from api.schemas.posts import PostResponse, StatsResponse
from api.utils.date_utils import get_day_boundaries

router = APIRouter()


@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    days: int = Query(30, ge=1, le=365, description="최근 N일 이내 게시글 조회"),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    게시글 목록 조회

    기본적으로 최근 30일 이내 크롤링된 게시글만 반환합니다.
    date_from 또는 date_to를 명시적으로 지정하면 days 파라미터는 무시됩니다.
    """
    query = select(Post).order_by(desc(Post.crawled_at))

    # date_from/date_to가 지정되지 않으면 기본 유효기간(days) 적용
    if not date_from and not date_to:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.where(Post.crawled_at >= cutoff_date)
    else:
        if date_from:
            query = query.where(Post.crawled_at >= date_from)
        if date_to:
            query = query.where(Post.crawled_at <= date_to)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    posts = result.scalars().all()

    return posts


@router.get("/posts/popular", response_model=List[PostResponse])
async def get_popular_posts(
    limit: int = Query(15, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
    gallery_id: Optional[str] = Query(None, description="갤러리 ID 필터 (wrtnai, aichatting, characterai)"),
    exclude_notices: bool = Query(True, description="공지사항 제외 여부"),
    db: AsyncSession = Depends(get_db)
):
    """
    인기 게시글 조회

    인기도 기준:
    - 추천수(recommend_count) 우선
    - 최근 N일 이내 크롤링된 데이터
    - 공지사항/안내글 자동 제외 (exclude_notices=True)
    - gallery_id 없으면 갤러리별 균등 쿼터 적용 (독점 방지)
    - 갤러리별 필터링 가능 (gallery_id)
    """
    # 기준 날짜 계산 (최근 N일)
    cutoff_date = datetime.now() - timedelta(days=days)

    # 공지사항 필터링 키워드 (제목에 포함 시 제외)
    notice_keywords = [
        '[필독]', '[공지]', '[안내]',
        '필독', '공지', '안내',
        '규칙', '이용규칙',
        '신고', '호출벨', '신문고',
        '전용', '통합',
        '디시콘', '공유전용'
    ]

    def filter_notices(posts, max_count):
        """공지사항 제외 후 max_count개 반환"""
        result = []
        for post in posts:
            if not any(kw in post.title for kw in notice_keywords):
                result.append(post)
                if len(result) >= max_count:
                    break
        return result

    # 특정 갤러리 지정 시: 기존 단일 갤러리 로직
    if gallery_id:
        query = select(Post).where(
            Post.crawled_at >= cutoff_date,
            Post.gallery_id == gallery_id
        ).order_by(desc(Post.recommend_count), desc(Post.view_count)).limit(limit * 5)
        result = await db.execute(query)
        all_posts = result.scalars().all()
        if exclude_notices:
            return filter_notices(all_posts, limit)
        return all_posts[:limit]

    # 전체 조회 시: 갤러리별 균등 쿼터제
    gallery_query = select(Post.gallery_id).where(
        Post.crawled_at >= cutoff_date
    ).distinct()
    gallery_result = await db.execute(gallery_query)
    gallery_ids = [r[0] for r in gallery_result.fetchall()]

    if not gallery_ids:
        return []

    # 갤러리당 쿼터: 전체 limit을 갤러리 수로 나눔 (최소 3개)
    per_gallery = max(3, limit // len(gallery_ids))
    fetch_per_gallery = per_gallery * 5  # 공지 필터 여유분

    combined = []
    for gid in gallery_ids:
        q = select(Post).where(
            Post.crawled_at >= cutoff_date,
            Post.gallery_id == gid
        ).order_by(desc(Post.recommend_count), desc(Post.view_count)).limit(fetch_per_gallery)
        r = await db.execute(q)
        posts = r.scalars().all()
        if exclude_notices:
            posts = filter_notices(posts, per_gallery)
        else:
            posts = list(posts[:per_gallery])
        combined.extend(posts)

    # 전체 합산 후 추천수 내림차순 정렬
    combined.sort(key=lambda p: (p.recommend_count, p.view_count), reverse=True)
    return combined[:limit]


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, db: AsyncSession = Depends(get_db)):
    """특정 게시글 조회"""
    result = await db.execute(select(Post).where(Post.post_id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")

    return post


@router.get("/posts/stats/daily", response_model=StatsResponse)
async def get_daily_stats(
    date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """일일 통계 조회"""
    target_date = date or datetime.now()
    start_of_day, end_of_day = get_day_boundaries(target_date)

    query = select(
        func.count(Post.id).label("total_posts"),
        func.coalesce(func.sum(Post.view_count), 0).label("total_views"),
        func.coalesce(func.sum(Post.recommend_count), 0).label("total_recommends"),
        func.coalesce(func.sum(Post.comment_count), 0).label("total_comments"),
        func.coalesce(func.avg(Post.view_count), 0).label("avg_views"),
        func.coalesce(func.avg(Post.recommend_count), 0).label("avg_recommends"),
        func.coalesce(func.avg(Post.comment_count), 0).label("avg_comments")
    ).where(
        Post.crawled_at >= start_of_day,
        Post.crawled_at < end_of_day
    )

    result = await db.execute(query)
    row = result.one()

    return StatsResponse(
        total_posts=row.total_posts,
        total_views=int(row.total_views),
        total_recommends=int(row.total_recommends),
        total_comments=int(row.total_comments),
        avg_views=round(float(row.avg_views), 1),
        avg_recommends=round(float(row.avg_recommends), 1),
        avg_comments=round(float(row.avg_comments), 1)
    )
