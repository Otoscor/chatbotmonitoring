"""
API 라우트 정의
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from models.database import get_db, AsyncSessionLocal, Post, DailyReport, CharacterMention, ChatServiceCharacter, NewsArticle, AppReview, Bookmark
from crawler.multi_crawler import crawl_all_targets
from crawler.character_service_crawler import crawl_all_character_services
from crawler.news_crawler import crawl_all_news
from analyzer.trend_analyzer import generate_daily_report

import logging
logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Pydantic 모델 ==========

class PostResponse(BaseModel):
    """게시글 응답 모델"""
    id: int
    post_id: str
    gallery_id: str
    title: str
    author: Optional[str]
    created_at: Optional[datetime]
    view_count: int
    recommend_count: int
    comment_count: int
    url: Optional[str]
    
    class Config:
        from_attributes = True


class KeywordResponse(BaseModel):
    """키워드 응답 모델"""
    keyword: str
    count: int
    score: float


class CharacterRankingResponse(BaseModel):
    """캐릭터 랭킹 응답 모델"""
    name: str
    mentions: int
    rank: int


class DailyReportResponse(BaseModel):
    """일일 리포트 응답 모델"""
    id: int
    report_date: datetime
    total_posts: int
    total_views: int
    total_recommends: int
    total_comments: int
    top_keywords: Optional[List[dict]]
    top_characters: Optional[List[dict]]
    trending_topics: Optional[List[dict]]
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """통계 응답 모델"""
    total_posts: int
    total_views: int
    total_recommends: int
    total_comments: int
    avg_views: float
    avg_recommends: float
    avg_comments: float


class CrawlRequest(BaseModel):
    """크롤링 요청 모델"""
    gallery_id: Optional[str] = None
    pages: Optional[int] = 5


class CrawlResponse(BaseModel):
    """크롤링 응답 모델"""
    success: bool
    message: str
    posts_count: int


class AppReviewResponse(BaseModel):
    """앱 리뷰 응답 모델"""
    id: int
    review_id: str
    app_name: str
    platform: str
    review_text: Optional[str]
    rating: int
    reviewer_name: Optional[str]
    review_date: Optional[datetime]
    crawled_at: datetime
    
    class Config:
        from_attributes = True


class AppReviewStatsResponse(BaseModel):
    """앱 리뷰 통계 응답 모델"""
    app_name: str
    total_reviews: int
    average_rating: float
    rating_distribution: dict  # {1: count, 2: count, ...}
    platform_distribution: dict  # {google_play: count, app_store: count}


# ========== 게시글 API ==========

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

    # ── 특정 갤러리 지정 시: 기존 단일 갤러리 로직 ──
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

    # ── 전체 조회 시: 갤러리별 균등 쿼터제 ──
    # 갤러리 목록 조회
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
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
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


# ========== 리포트 API ==========

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
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    start_of_day = target_date.replace(hour=0, minute=0, second=0)
    end_of_day = start_of_day + timedelta(days=1)
    
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
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    start_of_day = target_date.replace(hour=0, minute=0, second=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # 해당 날짜의 리포트 조회
    query = select(DailyReport).where(
        DailyReport.report_date >= start_of_day,
        DailyReport.report_date < end_of_day
    )
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report or not report.top_keywords:
        return []
    
    # top_keywords는 이미 [{"keyword": "xxx", "count": 10}, ...] 형식
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
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    start_of_day = target_date.replace(hour=0, minute=0, second=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # 해당 날짜의 리포트 조회
    query = select(DailyReport).where(
        DailyReport.report_date >= start_of_day,
        DailyReport.report_date < end_of_day
    )
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report or not report.top_characters:
        return []
    
    # top_characters는 이미 [{"name": "xxx", "mentions": 10}, ...] 형식
    return report.top_characters[:limit]


@router.get("/reports/{date}/tags")
async def get_report_tags(
    date: str,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """특정 날짜의 인기 해시태그 조회 (캐릭터챗 서비스)"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    start_of_day = target_date.replace(hour=0, minute=0, second=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # 해당 날짜에 크롤링된 캐릭터 데이터 조회
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
    from collections import Counter
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


# ========== 키워드/캐릭터 API ==========

@router.get("/keywords/trending")
async def get_trending_keywords(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """트렌딩 키워드 조회"""
    # 최근 N일간의 리포트에서 키워드 집계
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


# ========== 크롤링 API ==========

@router.post("/crawl", response_model=CrawlResponse)
async def trigger_crawl(
    request: CrawlRequest,
    db: AsyncSession = Depends(get_db)
):
    """수동 크롤링 트리거 - 모든 갤러리"""
    try:
        posts = await crawl_all_targets(pages=request.pages)
        
        # DB에 저장
        saved_count = 0
        for post_data in posts:
            # 중복 체크
            existing = await db.execute(
                select(Post).where(Post.post_id == post_data.post_id)
            )
            if existing.scalar_one_or_none():
                continue
            
            post = Post(
                post_id=post_data.post_id,
                gallery_id=post_data.gallery_id,
                title=post_data.title,
                author=post_data.author,
                created_at=post_data.created_at,
                view_count=post_data.view_count,
                recommend_count=post_data.recommend_count,
                comment_count=post_data.comment_count,
                url=post_data.url
            )
            db.add(post)
            saved_count += 1
        
        await db.commit()
        
        return CrawlResponse(
            success=True,
            message=f"크롤링 완료: {len(posts)}개 수집, {saved_count}개 저장",
            posts_count=saved_count
        )
    except Exception as e:
        return CrawlResponse(
            success=False,
            message=f"크롤링 실패: {str(e)}",
            posts_count=0
        )


@router.post("/reports/generate")
async def generate_report(
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """수동 리포트 생성"""
    if date:
        # 날짜가 지정된 경우
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
        
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # 지정된 날짜의 게시글 조회
        query = select(Post).where(
            Post.crawled_at >= start_of_day,
            Post.crawled_at < end_of_day
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        if not posts:
            raise HTTPException(status_code=404, detail="해당 날짜의 게시글이 없습니다")
    else:
        # 날짜가 지정되지 않은 경우: 최근 24시간 이내 크롤링된 게시글 사용
        since = datetime.now() - timedelta(hours=24)
        query = select(Post).where(
            Post.crawled_at >= since
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        if not posts:
            raise HTTPException(status_code=404, detail="최근 24시간 이내 크롤링된 게시글이 없습니다")
        
        # 가장 최근 크롤링 시간을 target_date로 설정
        target_date = datetime.now()
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
    
    # 이전 날짜 게시글 (비교용)
    prev_start = start_of_day - timedelta(days=1)
    prev_query = select(Post).where(
        Post.crawled_at >= prev_start,
        Post.crawled_at < start_of_day
    )
    prev_result = await db.execute(prev_query)
    prev_posts = prev_result.scalars().all()
    
    # 리포트 생성
    posts_dict = [
        {
            "title": p.title,
            "view_count": p.view_count,
            "recommend_count": p.recommend_count,
            "comment_count": p.comment_count
        }
        for p in posts
    ]
    prev_posts_dict = [
        {
            "title": p.title,
            "view_count": p.view_count,
            "recommend_count": p.recommend_count,
            "comment_count": p.comment_count
        }
        for p in prev_posts
    ]
    
    report_data = generate_daily_report(posts_dict, prev_posts_dict, target_date)
    
    # 기존 리포트 확인
    existing_query = select(DailyReport).where(
        DailyReport.report_date >= start_of_day,
        DailyReport.report_date < end_of_day
    )
    existing = await db.execute(existing_query)
    existing_report = existing.scalar_one_or_none()
    
    if existing_report:
        # 업데이트
        existing_report.total_posts = report_data["statistics"]["total_posts"]
        existing_report.total_views = report_data["statistics"]["total_views"]
        existing_report.total_recommends = report_data["statistics"]["total_recommends"]
        existing_report.total_comments = report_data["statistics"]["total_comments"]
        existing_report.top_keywords = report_data["top_keywords"]
        existing_report.top_characters = report_data["character_rankings"]
        existing_report.trending_topics = report_data["trending_topics"]
    else:
        # 새로 생성
        new_report = DailyReport(
            report_date=target_date,
            total_posts=report_data["statistics"]["total_posts"],
            total_views=report_data["statistics"]["total_views"],
            total_recommends=report_data["statistics"]["total_recommends"],
            total_comments=report_data["statistics"]["total_comments"],
            top_keywords=report_data["top_keywords"],
            top_characters=report_data["character_rankings"],
            trending_topics=report_data["trending_topics"]
        )
        db.add(new_report)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "리포트 생성 완료",
        "report": report_data
    }


# ========== 캐릭터챗 서비스 API ==========

class ChatServiceCharacterResponse(BaseModel):
    """캐릭터챗 서비스 캐릭터 응답 모델"""
    id: int
    service: str
    character_id: str
    rank: int
    name: str
    author: Optional[str]
    views: int
    tags: Optional[List[str]]
    description: Optional[str]
    thumbnail_url: Optional[str]
    character_url: Optional[str]
    crawled_at: datetime
    
    class Config:
        from_attributes = True


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
    # (동일 크롤링 세션에서 생성된 데이터를 모두 포함)
    time_threshold = recent_crawl_time - timedelta(minutes=5)
    
    query = select(ChatServiceCharacter).where(
        ChatServiceCharacter.crawled_at >= time_threshold,
        ChatServiceCharacter.crawled_at <= recent_crawl_time
    )
    
    if service:
        query = query.where(ChatServiceCharacter.service == service)
    
    # 각 서비스별로 rank 순서로 정렬 (알파벳 순이 아닌 rank 우선)
    query = query.order_by(
        ChatServiceCharacter.rank,
        ChatServiceCharacter.service
    ).limit(limit)
    
    result = await db.execute(query)
    characters = result.scalars().all()
    
    return characters


class CrawlChatServicesRequest(BaseModel):
    """캐릭터챗 서비스 크롤링 요청 모델"""
    services: Optional[List[str]] = None


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
    from collections import Counter
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


# ========== 뉴스 API ==========

class NewsArticleResponse(BaseModel):
    """뉴스 기사 응답 모델"""
    id: int
    article_id: str
    source: str
    title: str
    description: Optional[str]
    url: str
    publisher: Optional[str]
    published_at: Optional[datetime]
    crawled_at: datetime
    keyword: Optional[str]
    
    class Config:
        from_attributes = True


class CrawlNewsRequest(BaseModel):
    """뉴스 크롤링 요청 모델"""
    sources: Optional[List[str]] = None  # ['naver', 'google']
    keywords: Optional[List[str]] = None  # 사용자 정의 키워드


@router.get("/news", response_model=List[NewsArticleResponse])
async def get_news(
    source: Optional[str] = Query(None, description="소스 필터 (naver, google)"),
    keyword: Optional[str] = Query(None, description="키워드 필터"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    뉴스 기사 목록 조회
    최신 기사순으로 정렬
    """
    query = select(NewsArticle).order_by(desc(NewsArticle.published_at))
    
    if source:
        query = query.where(NewsArticle.source == source)
    if keyword:
        query = query.where(NewsArticle.keyword == keyword)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return articles


@router.get("/news/latest", response_model=List[NewsArticleResponse])
async def get_latest_news(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    최신 뉴스 기사 조회 (24시간 이내)
    """
    since = datetime.now() - timedelta(hours=24)
    
    query = select(NewsArticle).where(
        NewsArticle.crawled_at >= since
    ).order_by(desc(NewsArticle.published_at)).limit(limit)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return articles


@router.get("/news/sources")
async def get_news_sources(db: AsyncSession = Depends(get_db)):
    """
    뉴스 소스별 기사 수 조회
    """
    query = select(
        NewsArticle.source,
        func.count(NewsArticle.id).label("count")
    ).group_by(NewsArticle.source)
    
    result = await db.execute(query)
    sources = result.all()
    
    return [{"source": s.source, "count": s.count} for s in sources]


@router.post("/news/crawl")
async def crawl_news_endpoint(
    request: CrawlNewsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    뉴스 크롤링 트리거
    네이버 + 구글 뉴스 수집
    """
    try:
        # 크롤링 실행
        results = await crawl_all_news(
            sources=request.sources,
            keywords=request.keywords,
            limit_per_keyword=20
        )
        
        # DB에 저장 (중복 제거)
        saved_count = 0
        for source_name, articles in results.items():
            for article_data in articles:
                # 중복 체크
                existing = await db.execute(
                    select(NewsArticle).where(NewsArticle.article_id == article_data.article_id)
                )
                if existing.scalar_one_or_none():
                    continue
                
                article = NewsArticle(
                    article_id=article_data.article_id,
                    source=article_data.source,
                    title=article_data.title,
                    description=article_data.description,
                    url=article_data.url,
                    publisher=article_data.publisher,
                    published_at=article_data.published_at,
                    keyword=article_data.keyword
                )
                db.add(article)
                saved_count += 1
        
        await db.commit()
        
        total_crawled = sum(len(articles) for articles in results.values())
        
        return {
            "success": True,
            "message": f"뉴스 크롤링 완료: {total_crawled}개 수집, {saved_count}개 저장",
            "results": {
                source: len(articles) for source, articles in results.items()
            }
        }
    except Exception as e:
        logger.error(f"뉴스 크롤링 실패: {e}")
        return {
            "success": False,
            "message": f"크롤링 실패: {str(e)}",
            "results": {}
        }


# ========== 앱 리뷰 API ==========

@router.get("/app-reviews/today", response_model=List[AppReviewResponse])
async def get_today_app_reviews(
    db: AsyncSession = Depends(get_db)
):
    """오늘 크롤링한 리뷰 조회 (KST 기준 — crawled_at 기준)"""
    from zoneinfo import ZoneInfo
    
    # KST(UTC+9) 기준 오늘 날짜 계산
    kst = ZoneInfo("Asia/Seoul")
    now_kst = datetime.now(kst)
    start_of_day_kst = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day_kst = start_of_day_kst + timedelta(days=1)
    
    # DB는 UTC로 저장되므로 KST → UTC 변환
    start_of_day_utc = start_of_day_kst.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    end_of_day_utc = end_of_day_kst.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    
    # crawled_at이 오늘인 리뷰 조회 (리뷰 작성일은 어제 이전일 수 있음)
    query = select(AppReview).where(
        AppReview.crawled_at >= start_of_day_utc,
        AppReview.crawled_at < end_of_day_utc,
    ).order_by(AppReview.app_name, desc(AppReview.rating))
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return reviews


@router.get("/app-reviews", response_model=List[AppReviewResponse])
async def get_app_reviews(
    app_name: Optional[str] = Query(None, description="앱 이름 필터"),
    platform: Optional[str] = Query(None, description="플랫폼 필터 (google_play, app_store)"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="최소 평점"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """앱 리뷰 목록 조회"""
    query = select(AppReview).order_by(desc(AppReview.review_date))
    
    if app_name:
        query = query.where(AppReview.app_name == app_name)
    if platform:
        query = query.where(AppReview.platform == platform)
    if min_rating:
        query = query.where(AppReview.rating >= min_rating)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return reviews


@router.get("/app-reviews/stats", response_model=List[AppReviewStatsResponse])
async def get_app_review_stats(
    db: AsyncSession = Depends(get_db)
):
    """앱별 리뷰 통계"""
    # 앱별로 그룹화하여 통계 계산
    query = select(AppReview.app_name).distinct()
    result = await db.execute(query)
    app_names = result.scalars().all()
    
    stats_list = []
    
    for app_name in app_names:
        # 해당 앱의 모든 리뷰 조회
        app_reviews_query = select(AppReview).where(AppReview.app_name == app_name)
        app_reviews_result = await db.execute(app_reviews_query)
        app_reviews = app_reviews_result.scalars().all()
        
        if not app_reviews:
            continue
        
        # 통계 계산
        total_reviews = len(app_reviews)
        avg_rating = sum(r.rating for r in app_reviews) / total_reviews
        
        # 평점 분포
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in app_reviews:
            rating_dist[review.rating] = rating_dist.get(review.rating, 0) + 1
        
        # 플랫폼 분포
        platform_dist = {}
        for review in app_reviews:
            platform_dist[review.platform] = platform_dist.get(review.platform, 0) + 1
        
        stats_list.append(AppReviewStatsResponse(
            app_name=app_name,
            total_reviews=total_reviews,
            average_rating=round(avg_rating, 2),
            rating_distribution=rating_dist,
            platform_distribution=platform_dist
        ))
    
    return stats_list


@router.post("/app-reviews/crawl")
async def crawl_app_reviews(
    db: AsyncSession = Depends(get_db)
):
    """앱 리뷰 크롤링 트리거"""
    try:
        from crawler.app_review_crawler import AppReviewCrawler
        
        crawler = AppReviewCrawler()
        await crawler.crawl_all_apps(max_reviews_per_app=100)
        
        return {
            "success": True,
            "message": "앱 리뷰 크롤링이 완료되었습니다."
        }
    except Exception as e:
        logger.error(f"앱 리뷰 크롤링 실패: {e}")
        return {
            "success": False,
            "message": f"크롤링 실패: {str(e)}"
        }


@router.get("/app-reviews/keywords")
async def get_app_review_keywords(
    app_name: Optional[str] = Query(None, description="앱 이름 필터"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """앱 리뷰에서 가장 많이 나온 키워드 추출"""
    try:
        # 리뷰 조회
        query = select(AppReview.review_text).where(AppReview.review_text.isnot(None))
        
        if app_name:
            query = query.where(AppReview.app_name == app_name)
        
        result = await db.execute(query)
        reviews = result.scalars().all()
        
        if not reviews:
            return []
        
        # 간단한 키워드 추출 (한글/영문 단어)
        from collections import Counter
        import re
        
        word_counter = Counter()
        
        # 불용어 리스트 (의미없는 단어 제거)
        stopwords = {
            '그', '이', '저', '것', '수', '등', '들', '및', '를', '을', '가', '이', '은', '는', '하', '에', '의', '도', '로',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were',
            '있', '없', '되', '함', '하다', '있다', '없다', '같다', '와', '과', '네요', '요', '습니다', '이다'
        }
        
        for review_text in reviews:
            if not review_text:
                continue
            
            # 한글 단어 추출 (2자 이상)
            korean_words = re.findall(r'[가-힣]{2,}', review_text)
            # 영문 단어 추출 (2자 이상)
            english_words = re.findall(r'[a-zA-Z]{2,}', review_text.lower())
            
            # 단어 카운트
            for word in korean_words + english_words:
                if word not in stopwords and len(word) >= 2:
                    word_counter[word] += 1
        
        # 상위 N개 키워드 반환
        top_keywords = [
            {"keyword": word, "total_count": count}
            for word, count in word_counter.most_common(limit)
        ]
        
        return top_keywords
        
    except Exception as e:
        logger.error(f"리뷰 키워드 추출 실패: {e}")
        return []



# ========== 북마크 API ==========

class BookmarkCreate(BaseModel):
    """북마크 생성 요청"""
    url: str
    category: str = 'post'

class BookmarkUpdate(BaseModel):
    """북마크 수정 요청"""
    tags: Optional[List[str]] = None
    user_note: Optional[str] = None
    category: Optional[str] = None

class BookmarkResponse(BaseModel):
    """북마크 응답 모델"""
    id: int
    url: str
    title: Optional[str]
    description: Optional[str]
    ai_summary: Optional[str]
    thumbnail_url: Optional[str]
    site_name: Optional[str]
    category: str
    tags: Optional[List[str]]
    user_note: Optional[str]
    is_summarized: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark: BookmarkCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    북마크 추가
    
    URL을 즉시 저장하고, 메타데이터 추출 및 AI 요약은 백그라운드에서 처리합니다.
    (팝업/블로킹 문제 해결)
    """
    import asyncio
    
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
    # 주의: 요청 세션(db)은 종료되므로 사용 불가. 새 세션을 만들어야 함.
    asyncio.create_task(process_bookmark_background(new_bookmark.id, bookmark.url))
    
    return new_bookmark


async def process_bookmark_background(bookmark_id: int, url: str):
    """백그라운드에서 메타데이터 추출 및 AI 요약 수행"""
    from utils.url_parser import extract_url_metadata
    from utils.gemini_summarizer import summarize_url
    
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
            
            # 2. AI 요약 생성 (기능 제거됨)
            # summary = await summarize_url(url)
            
            # 다시 조회 (커밋 후 상태)
            if bookmark:
                bookmark.is_summarized = 1  # 요약 없이 완료 처리
                # bookmark.ai_summary = summary
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error processing bookmark {bookmark_id}: {e}")
            # 에러 상태 표시
            try:
                result = await session.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
                bookmark = result.scalar_one_or_none()
                if bookmark:
                    bookmark.is_summarized = 2
                    await session.commit()
            except Exception as db_err:
                logger.error(f"Failed to update error status: {db_err}")


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
    # 기능이 제거되었으므로 현재 상태 그대로 반환
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다")
    
    return bookmark

