import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { useApi } from '../hooks/useApi'
import KeywordCloud from '../components/KeywordCloud'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'

interface AppReview {
    id: number
    app_name: string
    platform: string
    review_text: string | null
    rating: number
    reviewer_name: string | null
    review_date: string | null
}

interface AppStats {
    app_name: string
    total_reviews: number
    average_rating: number
    rating_distribution: { [key: number]: number }
    platform_distribution: { [key: string]: number }
}



export default function AppReviews() {
    const [stats, setStats] = useState<AppStats[]>([])
    const [reviews, setReviews] = useState<AppReview[]>([])
    const [selectedApp, setSelectedApp] = useState<string>('')
    const [loading, setLoading] = useState(true)

    // 선택된 앱에 따라 키워드 가져오기
    const fetchKeywords = useCallback(async () => {
        if (!selectedApp) return []
        const response = await axios.get(`${API_URL}/app-reviews/keywords`, {
            params: { app_name: selectedApp, limit: 20 }
        })
        return response.data
    }, [selectedApp])

    const { data: keywords, loading: keywordsLoading } = useApi(fetchKeywords, [selectedApp])

    useEffect(() => {
        fetchStats()
    }, [])

    useEffect(() => {
        if (selectedApp) {
            fetchReviews(selectedApp)
        }
    }, [selectedApp])

    const fetchStats = async () => {
        try {
            setLoading(true)
            const response = await axios.get(`${API_URL}/app-reviews/stats`)
            setStats(response.data)
            if (response.data.length > 0) {
                setSelectedApp(response.data[0].app_name)
            }
        } catch (error) {
            console.error('Failed to fetch stats:', error)
        } finally {
            setLoading(false)
        }
    }

    const fetchReviews = async (appName: string) => {
        try {
            const response = await axios.get(`${API_URL}/app-reviews`, {
                params: { app_name: appName, limit: 100 }
            })
            setReviews(response.data)
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
            <div className="flex items-center justify-center py-12">
                <div className="text-sm text-gray-500">로딩 중...</div>
            </div>
        )
    }

    if (stats.length === 0) {
        return (
            <div className="py-12">
                <div className="text-center">
                    <p className="text-sm text-gray-500">아직 수집된 리뷰가 없습니다.</p>
                    <p className="text-xs text-gray-400 mt-1">크롤링을 실행하여 데이터를 수집해주세요.</p>
                </div>
            </div>
        )
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-semibold text-gray-900">앱 리뷰</h1>
                <p className="text-sm text-gray-500 mt-1">캐릭터 챗봇 앱의 사용자 리뷰 분석</p>
            </div>

            {/* 앱 선택 */}
            <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">앱 선택</label>
                <select
                    value={selectedApp}
                    onChange={(e) => setSelectedApp(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-200 rounded text-sm text-gray-900 focus:outline-none focus:border-gray-400"
                >
                    {stats.map((stat) => (
                        <option key={stat.app_name} value={stat.app_name} className="text-gray-900 bg-white">
                            {stat.app_name} ({stat.total_reviews}개 리뷰, 평점 {stat.average_rating.toFixed(1)})
                        </option>
                    ))}
                </select>
            </div>

            {/* 인기 키워드 */}
            <div className="bg-white border border-gray-200 rounded p-6 mb-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">리뷰에서 자주 언급된 키워드</h3>
                {keywordsLoading ? (
                    <div className="text-center py-8 text-sm text-gray-400">
                        데이터를 불러오는 중...
                    </div>
                ) : !keywords || keywords.length === 0 ? (
                    <div className="text-center py-8 text-sm text-gray-500">
                        키워드 데이터가 없습니다.
                    </div>
                ) : (
                    <KeywordCloud keywords={keywords} />
                )}
            </div>

            {/* 리뷰 목록 */}
            <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-3">
                    최근 리뷰 {reviews.length > 0 && `(${reviews.length}개)`}
                </h3>
                <div className="space-y-3">
                    {reviews.map((review) => (
                        <div key={review.id} className="bg-white border border-gray-200 rounded p-4">
                            <div className="flex items-start justify-between mb-2">
                                <div>
                                    <div className={`text-sm font-medium ${getRatingColor(review.rating)}`}>
                                        {getRatingStars(review.rating)}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        {review.reviewer_name || '익명'} · {review.platform === 'google_play' ? '구글 플레이' : '앱스토어'}
                                        {review.review_date && ` · ${new Date(review.review_date).toLocaleDateString()}`}
                                    </div>
                                </div>
                            </div>
                            {review.review_text && (
                                <p className="text-sm text-gray-700 leading-relaxed">{review.review_text}</p>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
