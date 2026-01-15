import axios from 'axios'

// 환경 변수에서 API URL 가져오기 (프로덕션) 또는 로컬 프록시 사용 (개발)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// 정적 데이터 모드 확인 (GitHub Pages 배포용)
export const USE_STATIC_DATA = import.meta.env.VITE_USE_STATIC_DATA === 'true'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2분으로 증가
  headers: {
    'Content-Type': 'application/json',
  },
})

// 정적 JSON 파일 fetch 헬퍼 함수
const fetchStaticData = async <T>(filename: string): Promise<T> => {
  const response = await fetch(`/data/${filename}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch ${filename}`)
  }
  return response.json()
}

// 타입 정의
export interface Post {
  id: number
  post_id: string
  gallery_id: string
  title: string
  author: string | null
  created_at: string | null
  view_count: number
  recommend_count: number
  comment_count: number
  url: string | null
}

export interface DailyReport {
  id: number
  report_date: string
  total_posts: number
  total_views: number
  total_recommends: number
  total_comments: number
  top_keywords: Array<{ keyword: string; count: number; score: number }>
  top_characters: Array<{ name: string; mentions: number; rank: number }>
  trending_topics: Array<{ topic: string; current: number; previous: number; growth: number }>
}

export interface Stats {
  total_posts: number
  total_views: number
  total_recommends: number
  total_comments: number
  avg_views: number
  avg_recommends: number
  avg_comments: number
}

export interface KeywordTrend {
  keyword: string
  total_count: number
  rank: number
}

export interface CharacterRanking {
  name: string
  total_mentions: number
  rank: number
}

export interface ChatServiceCharacter {
  id: number
  service: string
  character_id: string
  rank: number
  name: string
  author: string | null
  views: number
  tags: string[] | null
  description: string | null
  thumbnail_url: string | null
  character_url: string | null
  crawled_at: string
}

// API 함수들
export const fetchPosts = async (skip = 0, limit = 50): Promise<Post[]> => {
  if (USE_STATIC_DATA) {
    // 정적 모드에서는 인기 게시글만 반환
    return fetchPopularPosts(limit)
  }
  const { data } = await api.get('/posts', { params: { skip, limit } })
  return data
}

export const fetchPopularPosts = async (limit = 15, days = 7): Promise<Post[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<Post[]>('popular_posts.json')
  }
  const { data } = await api.get('/posts/popular', { params: { limit, days } })
  return data
}

export const fetchDailyStats = async (date?: string): Promise<Stats> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<Stats>('daily_stats.json')
  }
  const { data } = await api.get('/posts/stats/daily', { params: { date } })
  return data
}

export const fetchReports = async (skip = 0, limit = 30): Promise<DailyReport[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<DailyReport[]>('reports.json')
  }
  const { data } = await api.get('/reports', { params: { skip, limit } })
  return data
}

export const fetchLatestReport = async (): Promise<DailyReport> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<DailyReport>('latest_report.json')
  }
  const { data } = await api.get('/reports/latest')
  return data
}

export const fetchReportByDate = async (date: string): Promise<DailyReport> => {
  if (USE_STATIC_DATA) {
    // 정적 모드에서는 최신 리포트만 지원
    return fetchLatestReport()
  }
  const { data } = await api.get(`/reports/${date}`)
  return data
}

export const fetchTrendingKeywords = async (days = 7, limit = 20): Promise<KeywordTrend[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<KeywordTrend[]>('trending_keywords.json')
  }
  const { data } = await api.get('/keywords/trending', { params: { days, limit } })
  return data
}

export const fetchCharacterRanking = async (days = 7, limit = 20): Promise<CharacterRanking[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<CharacterRanking[]>('character_ranking.json')
  }
  const { data } = await api.get('/characters/ranking', { params: { days, limit } })
  return data
}

export const triggerCrawl = async (galleryId?: string, pages = 5) => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 크롤링을 사용할 수 없습니다.')
  }
  const { data } = await api.post('/crawl', { gallery_id: galleryId, pages })
  return data
}

export const generateReport = async (date?: string) => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 리포트 생성을 사용할 수 없습니다.')
  }
  const { data } = await api.post('/reports/generate', null, { params: { date } })
  return data
}

export const fetchChatServiceCharacters = async (service?: string, limit = 30): Promise<ChatServiceCharacter[]> => {
  if (USE_STATIC_DATA) {
    const allCharacters = await fetchStaticData<ChatServiceCharacter[]>('chat_characters.json')
    // 서비스 필터링
    if (service) {
      return allCharacters.filter(c => c.service === service).slice(0, limit)
    }
    return allCharacters.slice(0, limit)
  }
  const params: any = { limit }
  if (service) {
    params.service = service
  }
  const { data } = await api.get('/characters/chat-services', { params })
  return data
}

export const triggerChatServiceCrawl = async (services?: string[]) => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 크롤링을 사용할 수 없습니다.')
  }
  const { data } = await api.post('/characters/crawl-chat-services', { services })
  return data
}

export interface PopularTag {
  tag: string
  count: number
}

export const fetchPopularTags = async (limit = 20, service?: string): Promise<PopularTag[]> => {
  if (USE_STATIC_DATA) {
    const allTags = await fetchStaticData<PopularTag[]>('popular_tags.json')
    // 정적 모드에서는 서비스 필터링 미지원
    return allTags.slice(0, limit)
  }
  const params: any = { limit }
  if (service) params.service = service
  const { data } = await api.get('/characters/popular-tags', { params })
  return data
}

export default api
