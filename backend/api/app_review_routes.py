

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
