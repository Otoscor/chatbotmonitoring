"""
데이터 Export 스크립트
SQLite 데이터베이스에서 데이터를 읽어 JSON 파일로 변환
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import (
    Post, PostKeyword, DailyReport, CharacterMention, 
    ChatServiceCharacter, NewsArticle, Bookmark, AppReview, AsyncSessionLocal, init_db
)


async def export_latest_report(session: AsyncSession, output_dir: Path):
    """최신 일일 리포트 export"""
    print("📊 최신 리포트 export 중...")
    
    query = select(DailyReport).order_by(desc(DailyReport.report_date)).limit(1)
    result = await session.execute(query)
    report = result.scalar_one_or_none()
    
    if report:
        data = {
            "id": report.id,
            "report_date": report.report_date.isoformat(),
            "total_posts": report.total_posts,
            "total_views": report.total_views,
            "total_recommends": report.total_recommends,
            "total_comments": report.total_comments,
            "top_keywords": report.top_keywords or [],
            "top_characters": report.top_characters or [],
            "trending_topics": report.trending_topics or [],
        }
    else:
        data = None
    
    with open(output_dir / "latest_report.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ latest_report.json 생성")


async def export_reports(session: AsyncSession, output_dir: Path):
    """최근 30일 리포트 목록 export"""
    print("📊 리포트 목록 export 중...")
    
    query = select(DailyReport).order_by(desc(DailyReport.report_date)).limit(30)
    result = await session.execute(query)
    reports = result.scalars().all()
    
    data = []
    for report in reports:
        data.append({
            "id": report.id,
            "report_date": report.report_date.isoformat(),
            "total_posts": report.total_posts,
            "total_views": report.total_views,
            "total_recommends": report.total_recommends,
            "total_comments": report.total_comments,
            "top_keywords": report.top_keywords or [],
            "top_characters": report.top_characters or [],
            "trending_topics": report.trending_topics or [],
        })
    
    with open(output_dir / "reports.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ reports.json 생성 ({len(data)}개)")


async def export_popular_posts(session: AsyncSession, output_dir: Path):
    """인기 게시글 export (각 갤러리별 데이터 포함)"""
    print("📝 인기 게시글 export 중...")
    
    days_ago = datetime.utcnow() - timedelta(days=7)
    all_posts_map = {}  # 중복 제거를 위한 맵 {id: post_obj}

    # 1. 전체 인기 게시글 (기존 로직)
    query_all = (
        select(Post)
        .where(Post.created_at >= days_ago)
        .order_by(desc(Post.view_count))
        .limit(20)
    )
    result_all = await session.execute(query_all)
    for post in result_all.scalars().all():
        all_posts_map[post.id] = post

    # 2. 각 갤러리별 인기 게시글 추가 (필터링 시 데이터 부족 방지)
    target_galleries = ['wrtnai', 'aichatting', 'characterai']
    
    for gallery_id in target_galleries:
        query_gallery = (
            select(Post)
            .where(
                Post.created_at >= days_ago,
                Post.gallery_id == gallery_id
            )
            .order_by(desc(Post.view_count))
            .limit(15)
        )
        result_gallery = await session.execute(query_gallery)
        for post in result_gallery.scalars().all():
            all_posts_map[post.id] = post
    
    # 리스트로 변환 및 정렬 (전체 조회수 순)
    posts = list(all_posts_map.values())
    posts.sort(key=lambda x: x.view_count, reverse=True)
    
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "post_id": post.post_id,
            "gallery_id": post.gallery_id,
            "title": post.title,
            "author": post.author,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "view_count": post.view_count,
            "recommend_count": post.recommend_count,
            "comment_count": post.comment_count,
            "url": post.url,
        })
    
    with open(output_dir / "popular_posts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ popular_posts.json 생성 ({len(data)}개 - 갤러리별 확인 완료)")


async def export_chat_characters(session: AsyncSession, output_dir: Path):
    """챗봇 캐릭터 랭킹 export"""
    print("🤖 챗봇 캐릭터 export 중...")
    
    # 최근 크롤링 데이터 시간 확인
    recent_crawl_query = select(func.max(ChatServiceCharacter.crawled_at))
    result = await session.execute(recent_crawl_query)
    recent_crawl_time = result.scalar()
    
    if not recent_crawl_time:
        data = []
    else:
        # 최근 5분 이내의 데이터 조회
        time_threshold = recent_crawl_time - timedelta(minutes=5)
        
        query = (
            select(ChatServiceCharacter)
            .where(
                ChatServiceCharacter.crawled_at >= time_threshold,
                ChatServiceCharacter.crawled_at <= recent_crawl_time
            )
            .order_by(ChatServiceCharacter.service, ChatServiceCharacter.rank)
            .limit(300)
        )
        result = await session.execute(query)
        characters = result.scalars().all()
        
        data = []
        for char in characters:
            data.append({
                "id": char.id,
                "service": char.service,
                "character_id": char.character_id,
                "rank": char.rank,
                "name": char.name,
                "author": char.author,
                "views": char.views,
                "tags": char.tags or [],
                "description": char.description,
                "thumbnail_url": char.thumbnail_url,
                "character_url": char.character_url,
                "crawled_at": char.crawled_at.isoformat(),
            })
    
    with open(output_dir / "chat_characters.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ chat_characters.json 생성 ({len(data)}개)")


async def export_popular_tags(session: AsyncSession, output_dir: Path):
    """인기 해시태그 export"""
    print("🏷️  인기 해시태그 export 중...")
    
    # 최근 크롤링 데이터 시간 확인
    recent_crawl_query = select(func.max(ChatServiceCharacter.crawled_at))
    result = await session.execute(recent_crawl_query)
    recent_crawl_time = result.scalar()
    
    if not recent_crawl_time:
        data = []
    else:
        time_threshold = recent_crawl_time - timedelta(minutes=5)
        
        query = select(ChatServiceCharacter.tags).where(
            ChatServiceCharacter.crawled_at >= time_threshold,
            ChatServiceCharacter.crawled_at <= recent_crawl_time,
            ChatServiceCharacter.tags.isnot(None)
        )
        result = await session.execute(query)
        all_tags_lists = result.scalars().all()
        
        # 태그 카운트
        tag_counter = Counter()
        for tags_list in all_tags_lists:
            if tags_list and isinstance(tags_list, list):
                tag_counter.update(tags_list)
        
        data = [
            {"tag": tag, "count": count}
            for tag, count in tag_counter.most_common(20)
        ]
    
    with open(output_dir / "popular_tags.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ popular_tags.json 생성 ({len(data)}개)")


async def export_trending_keywords(session: AsyncSession, output_dir: Path):
    """트렌딩 키워드 export"""
    print("🔥 트렌딩 키워드 export 중...")
    
    # 최근 7일 키워드 집계
    days_ago = datetime.utcnow() - timedelta(days=7)
    
    query = (
        select(PostKeyword.keyword, func.count(PostKeyword.id).label('count'))
        .join(Post, Post.id == PostKeyword.post_id)
        .where(Post.created_at >= days_ago)
        .group_by(PostKeyword.keyword)
        .order_by(desc('count'))
        .limit(20)
    )
    result = await session.execute(query)
    keywords = result.all()
    
    data = []
    for idx, (keyword, count) in enumerate(keywords, 1):
        data.append({
            "keyword": keyword,
            "total_count": count,
            "rank": idx,
        })
    
    with open(output_dir / "trending_keywords.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ trending_keywords.json 생성 ({len(data)}개)")


async def export_character_ranking(session: AsyncSession, output_dir: Path):
    """캐릭터 언급 랭킹 export"""
    print("👥 캐릭터 랭킹 export 중...")
    
    # 최근 7일 캐릭터 언급 집계
    days_ago = datetime.utcnow() - timedelta(days=7)
    
    query = (
        select(
            CharacterMention.character_name,
            func.sum(CharacterMention.mention_count).label('total_mentions')
        )
        .where(CharacterMention.mention_date >= days_ago)
        .group_by(CharacterMention.character_name)
        .order_by(desc('total_mentions'))
        .limit(20)
    )
    result = await session.execute(query)
    characters = result.all()
    
    data = []
    for idx, (name, mentions) in enumerate(characters, 1):
        data.append({
            "name": name,
            "total_mentions": mentions,
            "rank": idx,
        })
    
    with open(output_dir / "character_ranking.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ character_ranking.json 생성 ({len(data)}개)")


async def export_daily_stats(session: AsyncSession, output_dir: Path):
    """일일 통계 export"""
    print("📈 일일 통계 export 중...")
    
    # 오늘 날짜로 통계 계산
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # 오늘의 게시글 통계
    query = select(
        func.count(Post.id).label('total_posts'),
        func.sum(Post.view_count).label('total_views'),
        func.sum(Post.recommend_count).label('total_recommends'),
        func.sum(Post.comment_count).label('total_comments'),
        func.avg(Post.view_count).label('avg_views'),
        func.avg(Post.recommend_count).label('avg_recommends'),
        func.avg(Post.comment_count).label('avg_comments'),
    ).where(
        Post.created_at >= today_start,
        Post.created_at <= today_end
    )
    result = await session.execute(query)
    row = result.first()
    
    if row:
        data = {
            "total_posts": row.total_posts or 0,
            "total_views": int(row.total_views or 0),
            "total_recommends": int(row.total_recommends or 0),
            "total_comments": int(row.total_comments or 0),
            "avg_views": float(row.avg_views or 0),
            "avg_recommends": float(row.avg_recommends or 0),
            "avg_comments": float(row.avg_comments or 0),
        }
    else:
        data = {
            "total_posts": 0,
            "total_views": 0,
            "total_recommends": 0,
            "total_comments": 0,
            "avg_views": 0,
            "avg_recommends": 0,
            "avg_comments": 0,
        }
    
    with open(output_dir / "daily_stats.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ daily_stats.json 생성")





async def export_news(session: AsyncSession, output_dir: Path):
    """뉴스 기사 export"""
    print("📰 뉴스 기사 export 중...")
    
    # 최근 30개 뉴스 기사 조회
    query = select(NewsArticle).order_by(desc(NewsArticle.crawled_at)).limit(30)
    result = await session.execute(query)
    articles = result.scalars(). all()
    
    data = []
    for article in articles:
        data.append({
            "id": article.id,
            "article_id": article.article_id,
            "source": article.source,
            "title": article.title,
            "description": article.description,
            "url": article.url,
            "publisher": article.publisher,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "crawled_at": article.crawled_at.isoformat(),
            "keyword": article.keyword,
        })
    
    with open(output_dir / "news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ news.json 생성 ({len(data)}개)")


async def export_bookmarks(session: AsyncSession, output_dir: Path):
    """북마크 export"""
    print("🔖 북마크 export 중...")
    
    # 모든 북마크 조회
    query = select(Bookmark).order_by(desc(Bookmark.created_at))
    result = await session.execute(query)
    bookmarks = result.scalars().all()
    
    data = []
    for bookmark in bookmarks:
        data.append({
            "id": bookmark.id,
            "url": bookmark.url,
            "title": bookmark.title,
            "description": bookmark.description,
            "ai_summary": bookmark.ai_summary,
            "thumbnail_url": bookmark.thumbnail_url,
            "site_name": bookmark.site_name,
            "tags": bookmark.tags or [],
            "user_note": bookmark.user_note,
            "is_summarized": bookmark.is_summarized,
            "created_at": bookmark.created_at.isoformat(),
            "updated_at": bookmark.updated_at.isoformat(),
        })
    
    with open(output_dir / "bookmarks.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ bookmarks.json 생성 ({len(data)}개)")
async def export_app_reviews(session: AsyncSession, output_dir: Path):
    """앱 리뷰 데이터 export"""
    print("📱 앱 리뷰 export 중...")
    
    # 1. 앱 통계 (app_stats.json)
    query = select(
        AppReview.app_name,
        func.count(AppReview.id).label('total_reviews'),
        func.avg(AppReview.rating).label('average_rating')
    ).group_by(AppReview.app_name).order_by(desc('total_reviews'))
    
    result = await session.execute(query)
    app_stats = result.all()
    
    # 각 앱별 통계 상세 계산
    stats_data = []
    
    for stat in app_stats:
        app_name = stat.app_name
        
        # 별점 분포
        rating_dist_query = select(
            AppReview.rating, 
            func.count(AppReview.id)
        ).where(AppReview.app_name == app_name).group_by(AppReview.rating)
        
        rating_dist_result = await session.execute(rating_dist_query)
        rating_dist = {r: c for r, c in rating_dist_result.all()}
        
        # 플랫폼 분포
        platform_dist_query = select(
            AppReview.platform,
            func.count(AppReview.id)
        ).where(AppReview.app_name == app_name).group_by(AppReview.platform)
        
        platform_dist_result = await session.execute(platform_dist_query)
        platform_dist = {p: c for p, c in platform_dist_result.all()}
        
        stats_data.append({
            "app_name": app_name,
            "total_reviews": stat.total_reviews,
            "average_rating": float(stat.average_rating or 0),
            "rating_distribution": rating_dist,
            "platform_distribution": platform_dist
        })
    
    with open(output_dir / "app_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ app_stats.json 생성 ({len(stats_data)} apps)")
    
    # 2. 전체 리뷰 (app_reviews.json)
    # 최근 500개 정도만 export
    reviews_query = select(AppReview).order_by(desc(AppReview.review_date)).limit(500)
    result = await session.execute(reviews_query)
    reviews = result.scalars().all()
    
    reviews_data = []
    for review in reviews:
        reviews_data.append({
            "id": review.id,
            "app_name": review.app_name,
            "platform": review.platform,
            "review_text": review.review_text,
            "rating": review.rating,
            "reviewer_name": review.reviewer_name,
            "review_date": review.review_date.isoformat() if review.review_date else None
        })
        
    with open(output_dir / "app_reviews.json", "w", encoding="utf-8") as f:
        json.dump(reviews_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ app_reviews.json 생성 ({len(reviews_data)} reviews)")
    
    # 3. 키워드 (app_keywords.json)
    # 간단하게 전체 키워드 뭉뚱그려서 빈 파일 또는 더미 생성 (키워드 추출 로직이 복잡하므로 여기선 생략하거나 간단히 구현)
    # 실제로는 형태소 분석 등이 필요하므로 여기서는 빈 리스트로 처리하거나 
    # 기존 API 로직을 가져와야 하지만, 의존성 문제로 인해 빈 리스트로 처리
    keywords_data = []
    with open(output_dir / "app_keywords.json", "w", encoding="utf-8") as f:
        json.dump(keywords_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ app_keywords.json 생성")


async def main():
    """메인 함수"""
    print("=" * 60)
    print("📦 데이터 Export 시작")
    print("=" * 60)
    
    # 출력 디렉토리 설정
    output_dir = Path(__file__).parent.parent / "frontend" / "public" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 출력 디렉토리: {output_dir}")
    print()
    
    # 데이터베이스 초기화
    await init_db()
    
    # 세션 생성
    async with AsyncSessionLocal() as session:
        try:
            # 각 데이터 export
            await export_latest_report(session, output_dir)
            await export_reports(session, output_dir)
            await export_popular_posts(session, output_dir)
            await export_chat_characters(session, output_dir)
            await export_popular_tags(session, output_dir)
            await export_trending_keywords(session, output_dir)
            await export_character_ranking(session, output_dir)
            await export_daily_stats(session, output_dir)
            await export_news(session, output_dir)
            await export_bookmarks(session, output_dir)
            await export_app_reviews(session, output_dir)
            
            print()
            print("=" * 60)
            print("✅ 모든 데이터 Export 완료!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Export 실패: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
