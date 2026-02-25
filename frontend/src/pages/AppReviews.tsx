import { useState, useEffect, useCallback, useMemo } from 'react'
import { useApi } from '../hooks/useApi'
import BubbleChart from '../components/BubbleChart'
import {
    fetchAppStats,
    fetchAppReviews,
    fetchAppKeywords,
    fetchTodayReviews,
    type AppStats,
    type AppReview
} from '../utils/api'

type TabId = 'today' | 'by-app'

export default function AppReviews() {
    const [stats, setStats] = useState<AppStats[]>([])
    const [reviews, setReviews] = useState<AppReview[]>([])
    const [todayReviews, setTodayReviews] = useState<AppReview[]>([])
    const [selectedApp, setSelectedApp] = useState<string>('')
    const [activeTab, setActiveTab] = useState<TabId>('today')
    const [openApps, setOpenApps] = useState<Set<string>>(new Set()) // 기본 모두 접힘
    const [loading, setLoading] = useState(true)

    const fetchKeywords = useCallback(() => fetchAppKeywords(selectedApp), [selectedApp])
    const { data: keywords, loading: keywordsLoading } = useApi(fetchKeywords, [selectedApp])

    useEffect(() => {
        loadStats()
        loadTodayReviews()
    }, [])

    // 오늘 데이터 없으면 앱별 조회 탭으로 자동 전환
    useEffect(() => {
        if (!loading && todayReviews.length === 0) {
            setActiveTab('by-app')
        }
    }, [loading, todayReviews.length])

    useEffect(() => {
        if (selectedApp) loadReviews(selectedApp)
    }, [selectedApp])

    const loadStats = async () => {
        try {
            setLoading(true)
            const data = await fetchAppStats()
            setStats(data)
            if (data.length > 0) setSelectedApp(data[0].app_name)
        } catch (error) {
            console.error('Failed to fetch stats:', error)
        } finally {
            setLoading(false)
        }
    }

    const loadTodayReviews = async () => {
        try {
            const data = await fetchTodayReviews()
            setTodayReviews(data)
        } catch (error) {
            console.error('Failed to fetch today reviews:', error)
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

    const todayReviewsByApp = useMemo(() => {
        const grouped: Record<string, AppReview[]> = {}
        for (const review of todayReviews) {
            if (!grouped[review.app_name]) grouped[review.app_name] = []
            grouped[review.app_name].push(review)
        }
        return grouped
    }, [todayReviews])

    const getRatingStars = (rating: number) => '★'.repeat(rating) + '☆'.repeat(5 - rating)

    const getRatingColor = (rating: number) => {
        if (rating >= 4) return 'text-gray-700'
        if (rating >= 3) return 'text-gray-600'
        return 'text-gray-400'
    }

    const ReviewCard = ({ review }: { review: AppReview }) => (
        <article className="review-card" data-review-id={review.id}>
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
            {review.review_text && <p className="review-text">{review.review_text}</p>}
        </article>
    )

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

    const hasTodayData = todayReviews.length > 0

    return (
        <div data-page="app-reviews">
            <header className="mb-6" data-section="header">
                <h1 className="page-title">앱 리뷰</h1>
                <p className="page-description mt-1">캐릭터 챗봇 앱의 사용자 리뷰 분석</p>
            </header>

            {/* 탭 헤더 */}
            <div className="flex gap-0 mb-6 border-b border-[var(--border-primary)]" data-section="tabs">
                {hasTodayData && (
                    <button
                        onClick={() => setActiveTab('today')}
                        className={`px-5 py-2.5 text-sm font-medium transition-colors relative ${activeTab === 'today'
                            ? 'text-[var(--text-primary)] after:absolute after:bottom-[-1px] after:left-0 after:right-0 after:h-[2px] after:bg-[var(--text-primary)] after:content-[\'\']'
                            : 'text-gray-400 hover:text-[var(--text-secondary)]'
                            }`}
                    >
                        <span className="flex items-center gap-1.5">
                            <span className="inline-block w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                            오늘 크롤링
                            <span className="text-xs text-gray-400">({todayReviews.length})</span>
                        </span>
                    </button>
                )}
                <button
                    onClick={() => setActiveTab('by-app')}
                    className={`px-5 py-2.5 text-sm font-medium transition-colors relative ${activeTab === 'by-app'
                        ? 'text-[var(--text-primary)] after:absolute after:bottom-[-1px] after:left-0 after:right-0 after:h-[2px] after:bg-[var(--text-primary)] after:content-[\'\']'
                        : 'text-gray-400 hover:text-[var(--text-secondary)]'
                        }`}
                >
                    앱별 조회
                </button>
            </div>

            {/* 탭: 오늘 크롤링 */}
            {activeTab === 'today' && hasTodayData && (
                <div data-section="today-reviews">
                    <p className="text-xs text-gray-400 mb-5">
                        {new Date().toLocaleDateString('ko-KR')} 크롤링된 리뷰 · 총 {todayReviews.length}개
                    </p>
                    <div className="space-y-2">
                        {Object.entries(todayReviewsByApp).map(([appName, appReviews]) => {
                            const isOpen = openApps.has(appName)
                            const avgRating = (appReviews.reduce((s, r) => s + r.rating, 0) / appReviews.length).toFixed(1)
                            const toggle = () => setOpenApps(prev => {
                                const next = new Set(prev)
                                isOpen ? next.delete(appName) : next.add(appName)
                                return next
                            })
                            return (
                                <div key={appName} className="border border-[var(--border-primary)] rounded-lg">
                                    {/* 아코디언 헤더 — sticky */}
                                    <button
                                        onClick={toggle}
                                        className={`sticky top-[56px] md:top-0 z-20 w-full flex items-center justify-between px-4 py-3 bg-[var(--bg-secondary)] hover:opacity-80 transition-opacity text-left border-b border-[var(--border-primary)] ${isOpen ? 'rounded-t-lg' : 'rounded-lg'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <h4 className="text-sm font-semibold text-[var(--text-primary)]">{appName}</h4>
                                            <span className="text-xs text-gray-400">{appReviews.length}개 리뷰</span>
                                            <span className="text-xs text-gray-400">· 평균 ★{avgRating}</span>
                                        </div>
                                        <svg
                                            className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                                            fill="none" viewBox="0 0 24 24" stroke="currentColor"
                                        >
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                        </svg>
                                    </button>
                                    {/* 아코디언 콘텐츠 */}
                                    {isOpen && (
                                        <div className="px-4 py-3 space-y-2 rounded-b-lg">
                                            {appReviews.map((review) => (
                                                <ReviewCard key={review.id} review={review} />
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* 탭: 앱별 조회 */}
            {activeTab === 'by-app' && (
                <div data-section="by-app">
                    {/* 앱 선택 */}
                    <section className="mb-6 sticky md:static top-[56px] z-30 bg-[var(--bg-primary)] py-4 -mx-4 px-4 border-b border-[var(--border-primary)] shadow-sm md:shadow-none md:border-none md:p-0 md:m-0 transition-all" data-section="app-selector">
                        <label className="form-label">앱 선택</label>
                        <select
                            value={selectedApp}
                            onChange={(e) => setSelectedApp(e.target.value)}
                            className="form-select"
                            data-component="app-select"
                        >
                            {stats.map((stat) => (
                                <option key={stat.app_name} value={stat.app_name}>
                                    {stat.app_name} ({stat.total_reviews}개 리뷰, 평점 {stat.average_rating.toFixed(1)})
                                </option>
                            ))}
                        </select>
                    </section>

                    {/* 인기 키워드 */}
                    <section className="card p-6 mb-6 relative" data-section="review-keywords">
                        <h3 className="section-title mb-4">리뷰에서 자주 언급된 키워드</h3>
                        {keywordsLoading ? (
                            <div className="empty-state" data-state="loading">데이터를 불러오는 중...</div>
                        ) : !keywords || keywords.length === 0 ? (
                            <div className="empty-state" data-state="empty">키워드 데이터가 없습니다.</div>
                        ) : (
                            <>
                                <BubbleChart
                                    keywords={keywords.map(k => {
                                        let sentiment = k.sentiment_score
                                        if (typeof sentiment === 'undefined') {
                                            const hash = k.keyword.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
                                            sentiment = (hash % 200 - 100) / 100
                                        }
                                        return { text: k.keyword, value: k.total_count, sentiment }
                                    })}
                                />
                                <div className="absolute bottom-4 right-4 flex gap-3 pointer-events-none select-none opacity-60">
                                    <span className="text-[12px] text-gray-500 dark:text-gray-400 font-medium">마우스 휠 확대/축소</span>
                                    <span className="text-[12px] text-gray-500 dark:text-gray-400 font-medium">마우스 패닝 이동</span>
                                </div>
                            </>
                        )}
                    </section>

                    {/* 리뷰 목록 */}
                    <section data-section="reviews-list">
                        <h3 className="section-title mb-3">
                            최근 리뷰 {reviews.length > 0 && `(${reviews.length}개)`}
                        </h3>
                        <div className="space-y-3">
                            {reviews.map((review) => (
                                <ReviewCard key={review.id} review={review} />
                            ))}
                        </div>
                    </section>
                </div>
            )}
        </div>
    )
}
