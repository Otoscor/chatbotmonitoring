/**
 * 앱 리뷰 페이지 상태 관리 훅
 */
import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  fetchAppStats,
  fetchAppReviews,
  fetchTodayReviews,
  type AppStats,
  type AppReview
} from '../../../utils/api'

export type TabId = 'today' | 'by-app'

interface UseAppReviewsReturn {
  // 상태
  stats: AppStats[]
  reviews: AppReview[]
  todayReviews: AppReview[]
  selectedApp: string
  activeTab: TabId
  openApps: Set<string>
  loading: boolean

  // 계산된 값
  todayReviewsByApp: Record<string, AppReview[]>
  hasTodayData: boolean

  // 액션
  setSelectedApp: (app: string) => void
  setActiveTab: (tab: TabId) => void
  toggleAppOpen: (appName: string) => void
}

export function useAppReviews(): UseAppReviewsReturn {
  // 상태
  const [stats, setStats] = useState<AppStats[]>([])
  const [reviews, setReviews] = useState<AppReview[]>([])
  const [todayReviews, setTodayReviews] = useState<AppReview[]>([])
  const [selectedApp, setSelectedApp] = useState<string>('')
  const [activeTab, setActiveTab] = useState<TabId>('today')
  const [openApps, setOpenApps] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)

  // 초기 데이터 로드
  const loadStats = useCallback(async () => {
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
  }, [])

  const loadTodayReviews = useCallback(async () => {
    try {
      const data = await fetchTodayReviews()
      setTodayReviews(data)
    } catch (error) {
      console.error('Failed to fetch today reviews:', error)
    }
  }, [])

  const loadReviews = useCallback(async (appName: string) => {
    try {
      const data = await fetchAppReviews(appName)
      setReviews(data)
    } catch (error) {
      console.error('Failed to fetch reviews:', error)
    }
  }, [])

  // 초기 로드
  useEffect(() => {
    loadStats()
    loadTodayReviews()
  }, [loadStats, loadTodayReviews])

  // 오늘 데이터 없으면 앱별 조회 탭으로 자동 전환
  useEffect(() => {
    if (!loading && todayReviews.length === 0) {
      setActiveTab('by-app')
    }
  }, [loading, todayReviews.length])

  // 앱 선택 시 리뷰 로드
  useEffect(() => {
    if (selectedApp) loadReviews(selectedApp)
  }, [selectedApp, loadReviews])

  // 오늘 리뷰를 앱별로 그룹화
  const todayReviewsByApp = useMemo(() => {
    const grouped: Record<string, AppReview[]> = {}
    for (const review of todayReviews) {
      if (!grouped[review.app_name]) grouped[review.app_name] = []
      grouped[review.app_name].push(review)
    }
    return grouped
  }, [todayReviews])

  // 앱 아코디언 토글
  const toggleAppOpen = useCallback((appName: string) => {
    setOpenApps(prev => {
      const next = new Set(prev)
      if (next.has(appName)) {
        next.delete(appName)
      } else {
        next.add(appName)
      }
      return next
    })
  }, [])

  const hasTodayData = todayReviews.length > 0

  return {
    // 상태
    stats,
    reviews,
    todayReviews,
    selectedApp,
    activeTab,
    openApps,
    loading,

    // 계산된 값
    todayReviewsByApp,
    hasTodayData,

    // 액션
    setSelectedApp,
    setActiveTab,
    toggleAppOpen
  }
}
