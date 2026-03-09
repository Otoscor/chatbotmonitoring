

# ========== 앱 리뷰 API ==========

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
    """앱별 리뷰 통계 (최적화: N+1 문제 해결 - 3개의 집계 쿼리로 처리)"""
    from sqlalchemy import func

    # 1. 기본 통계: 앱별 총 리뷰 수, 평균 평점 (단일 쿼리)
    base_stats_query = select(
        AppReview.app_name,
        func.count(AppReview.id).label('total_reviews'),
        func.avg(AppReview.rating).label('avg_rating')
    ).group_by(AppReview.app_name)

    base_result = await db.execute(base_stats_query)
    base_stats = {row.app_name: {
        'total_reviews': row.total_reviews,
        'avg_rating': round(float(row.avg_rating), 2) if row.avg_rating else 0
    } for row in base_result}

    # 2. 평점 분포: 앱별, 평점별 카운트 (단일 쿼리)
    rating_dist_query = select(
        AppReview.app_name,
        AppReview.rating,
        func.count(AppReview.id).label('count')
    ).group_by(AppReview.app_name, AppReview.rating)

    rating_result = await db.execute(rating_dist_query)
    rating_dist = {}
    for row in rating_result:
        if row.app_name not in rating_dist:
            rating_dist[row.app_name] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        rating_dist[row.app_name][row.rating] = row.count

    # 3. 플랫폼 분포: 앱별, 플랫폼별 카운트 (단일 쿼리)
    platform_dist_query = select(
        AppReview.app_name,
        AppReview.platform,
        func.count(AppReview.id).label('count')
    ).group_by(AppReview.app_name, AppReview.platform)

    platform_result = await db.execute(platform_dist_query)
    platform_dist = {}
    for row in platform_result:
        if row.app_name not in platform_dist:
            platform_dist[row.app_name] = {}
        platform_dist[row.app_name][row.platform] = row.count

    # 결과 조합
    stats_list = []
    for app_name, stats in base_stats.items():
        stats_list.append(AppReviewStatsResponse(
            app_name=app_name,
            total_reviews=stats['total_reviews'],
            average_rating=stats['avg_rating'],
            rating_distribution=rating_dist.get(app_name, {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}),
            platform_distribution=platform_dist.get(app_name, {})
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
