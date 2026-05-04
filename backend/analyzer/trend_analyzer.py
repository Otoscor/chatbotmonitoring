"""
트렌드 분석 모듈
- 일별 통계 계산
- 트렌드 감지
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import logging

from .keyword_extractor import extract_keywords, extract_keywords_tfidf
from .character_ranker import rank_characters, analyze_character_trends

logger = logging.getLogger(__name__)


def calculate_daily_stats(posts: List[Dict]) -> Dict[str, any]:
    """
    일일 통계 계산
    
    Args:
        posts: 게시글 목록 [{"title": "", "view_count": 0, ...}, ...]
        
    Returns:
        {
            "total_posts": 100,
            "total_views": 10000,
            "total_recommends": 500,
            "total_comments": 200,
            "avg_views": 100,
            "avg_recommends": 5,
            "avg_comments": 2
        }
    """
    if not posts:
        return {
            "total_posts": 0,
            "total_views": 0,
            "total_recommends": 0,
            "total_comments": 0,
            "avg_views": 0,
            "avg_recommends": 0,
            "avg_comments": 0
        }
    
    total_posts = len(posts)
    total_views = sum(p.get("view_count", 0) for p in posts)
    total_recommends = sum(p.get("recommend_count", 0) for p in posts)
    total_comments = sum(p.get("comment_count", 0) for p in posts)
    
    return {
        "total_posts": total_posts,
        "total_views": total_views,
        "total_recommends": total_recommends,
        "total_comments": total_comments,
        "avg_views": round(total_views / total_posts, 1),
        "avg_recommends": round(total_recommends / total_posts, 1),
        "avg_comments": round(total_comments / total_posts, 1)
    }


def find_trending_topics(
    current_keywords: List[Dict],
    previous_keywords: List[Dict],
    threshold: float = 50.0
) -> List[Dict[str, any]]:
    """
    급상승 토픽 감지
    
    Args:
        current_keywords: 현재 기간 키워드
        previous_keywords: 이전 기간 키워드
        threshold: 상승률 임계값 (%)
        
    Returns:
        [{"topic": "xxx", "current": 10, "previous": 2, "growth": 400.0}, ...]
    """
    current_dict = {k["keyword"]: k["count"] for k in current_keywords}
    previous_dict = {k["keyword"]: k["count"] for k in previous_keywords}
    
    all_keywords = set(current_dict.keys()) | set(previous_dict.keys())
    
    trending = []
    for keyword in all_keywords:
        current = current_dict.get(keyword, 0)
        previous = previous_dict.get(keyword, 0)
        
        # 성장률 계산
        if previous > 0:
            growth = ((current - previous) / previous) * 100
        elif current >= 3:  # 새로 등장하고 최소 3회 이상 언급
            growth = 100.0
        else:
            continue
        
        if growth >= threshold and current >= 3:
            trending.append({
                "topic": keyword,
                "current": current,
                "previous": previous,
                "growth": round(growth, 1)
            })
    
    # 성장률 기준 정렬
    trending.sort(key=lambda x: x["growth"], reverse=True)
    
    return trending[:20]


def identify_hot_posts(posts: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    인기 게시글 식별 (조회수 + 추천수 + 댓글 수 종합)
    
    Args:
        posts: 게시글 목록
        top_n: 반환할 상위 개수
        
    Returns:
        상위 인기 게시글 목록
    """
    def calculate_score(post: Dict) -> float:
        """인기도 점수 계산"""
        view_weight = 1.0
        recommend_weight = 10.0
        comment_weight = 5.0
        
        return (
            post.get("view_count", 0) * view_weight +
            post.get("recommend_count", 0) * recommend_weight +
            post.get("comment_count", 0) * comment_weight
        )
    
    scored_posts = [(post, calculate_score(post)) for post in posts]
    scored_posts.sort(key=lambda x: x[1], reverse=True)
    
    result = []
    for post, score in scored_posts[:top_n]:
        result.append({
            **post,
            "popularity_score": round(score, 1)
        })
    
    return result


def generate_daily_report(
    posts: List[Dict],
    previous_posts: Optional[List[Dict]] = None,
    report_date: datetime = None
) -> Dict[str, any]:
    """
    일일 리포트 생성
    
    Args:
        posts: 오늘 수집된 게시글
        previous_posts: 이전 기간 게시글 (트렌드 비교용)
        report_date: 리포트 날짜
        
    Returns:
        완성된 일일 리포트
    """
    report_date = report_date or datetime.now()
    
    # 기본 통계
    stats = calculate_daily_stats(posts)
    
    # 게시글 제목 추출
    titles = [p.get("title", "") for p in posts if p.get("title")]
    previous_titles = [p.get("title", "") for p in (previous_posts or []) if p.get("title")]
    
    # 키워드 추출
    keywords = extract_keywords_tfidf(titles, top_n=30)
    
    # 캐릭터 랭킹
    character_rankings = rank_characters(titles, top_n=20)
    
    # 트렌드 분석 (이전 데이터가 있는 경우)
    trending_topics = []
    character_trends = []
    
    if previous_posts:
        previous_keywords = extract_keywords_tfidf(previous_titles, top_n=30)
        trending_topics = find_trending_topics(keywords, previous_keywords)
        character_trends = analyze_character_trends(titles, previous_titles)
    
    # 인기 게시글
    hot_posts = identify_hot_posts(posts, top_n=10)
    
    report = {
        "report_date": report_date.isoformat(),
        "generated_at": datetime.now().isoformat(),
        "statistics": stats,
        "top_keywords": keywords,
        "character_rankings": character_rankings,
        "trending_topics": trending_topics,
        "character_trends": character_trends,
        "hot_posts": hot_posts,
        "summary": generate_summary(stats, keywords, character_rankings)
    }
    
    return report


def generate_summary(
    stats: Dict,
    keywords: List[Dict],
    characters: List[Dict]
) -> str:
    """리포트 요약 텍스트 생성"""
    top_keywords_str = ", ".join([k["keyword"] for k in keywords[:5]])
    top_characters_str = ", ".join([c["name"] for c in characters[:5]])
    
    summary = f"""
오늘 총 {stats['total_posts']}개의 게시글이 수집되었습니다.
총 조회수 {stats['total_views']:,}회, 추천 {stats['total_recommends']}개, 댓글 {stats['total_comments']}개가 기록되었습니다.

주요 키워드: {top_keywords_str}
인기 캐릭터: {top_characters_str}
""".strip()
    
    return summary


async def save_report_to_db(report: Dict, session) -> None:
    """리포트를 데이터베이스에 저장"""
    from models.database import DailyReport
    from datetime import datetime
    
    report_date = datetime.fromisoformat(report["report_date"])
    
    db_report = DailyReport(
        report_date=report_date,
        total_posts=report["statistics"]["total_posts"],
        total_views=report["statistics"]["total_views"],
        total_recommends=report["statistics"]["total_recommends"],
        total_comments=report["statistics"]["total_comments"],
        top_keywords=report["top_keywords"],
        top_characters=report["character_rankings"],
        trending_topics=report["trending_topics"]
    )
    
    session.add(db_report)
    await session.commit()
