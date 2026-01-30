import { useState, useEffect, useCallback } from 'react'
import { useApi } from '../hooks/useApi'
import KeywordCloud from '../components/KeywordCloud'
import {
    fetchAppStats,
    fetchAppReviews,
    fetchAppKeywords,
    type AppStats,
    type AppReview
} from '../utils/api'

export default function AppReviews() {
    const [stats, setStats] = useState<AppStats[]>([])
    const [reviews, setReviews] = useState<AppReview[]>([])
    const [selectedApp, setSelectedApp] = useState<string>('')
    const [loading, setLoading] = useState(true)

    // 선택된 앱에 따라 키워드 가져오기
    const fetchKeywords = useCallback(() => fetchAppKeywords(selectedApp), [selectedApp])

    const { data: keywords, loading: keywordsLoading } = useApi(fetchKeywords, [selectedApp])

    useEffect(() => {
        loadStats()
    }, [])

    useEffect(() => {
        if (selectedApp) {
            loadReviews(selectedApp)
        }
    }, [selectedApp])

    const loadStats = async () => {
        try {
            setLoading(true)
            const data = await fetchAppStats()
            setStats(data)
            if (data.length > 0) {
                setSelectedApp(data[0].app_name)
            }
        } catch (error) {
            console.error('Failed to fetch stats:', error)
        } finally {
            setLoading(false)
        }
    }

    const loadReviews = async (appName: string) => {
        try {
            const data = await fetchAppReviews(appName)
            setReviews(data)
        } catch (error) {
            console.error('Failed to fetch reviews:', error)
        }
    }

    const getRatingStars = (rating: number) => {
        return '★'.repeat(rating) + '☆'.repeat(5 - rating)
    }

    const getRatingColor = (rating: number) => {
        if (rating >= 4) return 'text-gray-700'
        if (rating >= 3) return 'text-gray-600'
        return 'text-gray-400'
    }

    if (loading) {
        return (
            <div className="loading-state py-12" data-state="loading">
                <div className="loading-text">로딩 중...</div>
            </div>
        )
    }

    if (stats.length === 0) {
        return (
            <div className="py-12" data-state="no-data">
                <div className="text-center">
                    <p className="text-sm text-gray-500">아직 수집된 리뷰가 없습니다.</p>
                    <p className="text-xs text-gray-400 mt-1">크롤링을 실행하여 데이터를 수집해주세요.</p>
                </div>
            </div>
        )
    }

    return (
        <div data-page="app-reviews">
            <header className="mb-8" data-section="header">
                <h1 className="page-title">앱 리뷰</h1>
                <p className="page-description mt-1">캐릭터 챗봇 앱의 사용자 리뷰 분석</p>
            </header>

            {/* 앱 선택 */}
            <section className="mb-6" data-section="app-selector">
                <label className="block text-sm font-medium text-gray-700 mb-2 dark:text-gray-300">앱 선택</label>
                <select
                    value={selectedApp}
                    onChange={(e) => setSelectedApp(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded text-sm text-gray-900 focus:outline-none focus:border-gray-400 dark:bg-[#1a1a1a] dark:border-gray-700 dark:text-white dark:focus:border-gray-500"
                    data-component="app-select"
                >
                    {stats.map((stat) => (
                        <option key={stat.app_name} value={stat.app_name} className="text-gray-900 bg-white dark:bg-[#1a1a1a] dark:text-white">
                            {stat.app_name} ({stat.total_reviews}개 리뷰, 평점 {stat.average_rating.toFixed(1)})
                        </option>
                    ))}
                </select>
            </section>

            {/* 인기 키워드 */}
            <section className="card p-6 mb-6" data-section="review-keywords">
                <h3 className="section-title mb-4">리뷰에서 자주 언급된 키워드</h3>
                {keywordsLoading ? (
                    <div className="empty-state" data-state="loading">
                        데이터를 불러오는 중...
                    </div>
                ) : !keywords || keywords.length === 0 ? (
                    <div className="empty-state" data-state="empty">
                        키워드 데이터가 없습니다.
                    </div>
                ) : (
                    <KeywordCloud
                        keywords={keywords?.map(k => ({
                            text: k.keyword,
                            value: k.total_count
                        })) || []}
                    />
                )}
            </section>

            {/* 리뷰 목록 */}
            <section data-section="reviews-list">
                <h3 className="section-title mb-3">
                    최근 리뷰 {reviews.length > 0 && `(${reviews.length}개)`}
                </h3>
                <div className="space-y-3">
                    {reviews.map((review) => (
                        <article
                            key={review.id}
                            className="review-card"
                            data-review-id={review.id}
                        >
                            <div className="flex items-start justify-between mb-2">
                                <div>
                                    <div className={`review-rating ${getRatingColor(review.rating)}`}>
                                        {getRatingStars(review.rating)}
                                    </div>
                                    <div className="review-meta">
                                        {review.reviewer_name || '익명'} · {review.platform === 'google_play' ? '구글 플레이' : '앱스토어'}
                                        {review.review_date && ` · ${new Date(review.review_date).toLocaleDateString()}`}
                                    </div>
                                </div>
                            </div>
                            {review.review_text && (
                                <p className="review-text">{review.review_text}</p>
                            )}
                        </article>
                    ))}
                </div>
            </section>
        </div>
    )
}
