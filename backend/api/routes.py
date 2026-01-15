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

from models.database import get_db, Post, DailyReport, CharacterMention, ChatServiceCharacter
from crawler.multi_crawler import crawl_all_targets
from crawler.character_service_crawler import crawl_all_character_services
from analyzer.trend_analyzer import generate_daily_report

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


# ========== 게시글 API ==========

@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """게시글 목록 조회"""
    query = select(Post).order_by(desc(Post.crawled_at))
    
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
    exclude_notices: bool = Query(True, description="공지사항 제외 여부"),
    db: AsyncSession = Depends(get_db)
):
    """
    인기 게시글 조회
    
    인기도 기준:
    - 추천수(recommend_count) 우선
    - 최근 N일 이내 크롤링된 데이터
    - 공지사항/안내글 자동 제외 (exclude_notices=True)
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
    
    # 더 많은 게시글을 가져와서 필터링 (limit * 5)
    query = select(Post).where(
        Post.crawled_at >= cutoff_date
    ).order_by(
        desc(Post.recommend_count),
        desc(Post.view_count)
    ).limit(limit * 5)
    
    result = await db.execute(query)
    all_posts = result.scalars().all()
    
    # 공지사항 필터링
    if exclude_notices:
        filtered_posts = []
        for post in all_posts:
            # 제목에 공지 키워드가 포함되어 있는지 확인
            is_notice = any(keyword in post.title for keyword in notice_keywords)
            if not is_notice:
                filtered_posts.append(post)
                if len(filtered_posts) >= limit:
                    break
        return filtered_posts
    else:
        return all_posts[:limit]


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
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
    
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # 오늘 게시글 조회
    query = select(Post).where(
        Post.crawled_at >= start_of_day,
        Post.crawled_at < end_of_day
    )
    result = await db.execute(query)
    posts = result.scalars().all()
    
    if not posts:
        raise HTTPException(status_code=404, detail="해당 날짜의 게시글이 없습니다")
    
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
    service: Optional[str] = Query(None, description="서비스 필터 (zeta, babechat)"),
    limit: int = Query(30, ge=1, le=100),
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
    
    query = query.order_by(
        ChatServiceCharacter.service,
        ChatServiceCharacter.rank
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
