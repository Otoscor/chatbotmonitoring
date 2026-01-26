import axios from 'axios'

// 환경 변수에서 API URL 가져오기 (프로덕션) 또는 로컬 프록시 사용 (개발)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// API URL export (다른 컴포넌트에서 사용)
export const API_URL = API_BASE_URL

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
// GitHub Pages base path 고려
const getBasePath = () => {
  // Vite의 base path를 가져오거나 기본값 사용
  return import.meta.env.BASE_URL || '/'
}

const fetchStaticData = async <T>(filename: string): Promise<T> => {
  const basePath = getBasePath()
  const url = `${basePath}data/${filename}`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`Failed to fetch ${filename} from ${url}`)
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

export const fetchPopularPosts = async (limit = 15, days = 7, galleryId?: string): Promise<Post[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<Post[]>('popular_posts.json')
  }
  const params: any = { limit, days }
  if (galleryId) {
    params.gallery_id = galleryId
  }
  const { data } = await api.get('/posts/popular', { params })
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

export const fetchChatServiceCharacters = async (service?: string, limit = 150): Promise<ChatServiceCharacter[]> => {
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

// 날짜별 리포트 상세 데이터
export interface ReportKeyword {
  text: string
  value: number
}

export interface ReportCharacter {
  name: string
  mentions: number
}

export const fetchReportKeywords = async (date: string, limit = 20): Promise<ReportKeyword[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<ReportKeyword[]>('trending_keywords.json')
  }
  const { data } = await api.get(`/reports/${date}/keywords`, { params: { limit } })
  return data
}

export const fetchReportCharacters = async (date: string, limit = 20): Promise<ReportCharacter[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<ReportCharacter[]>('character_ranking.json')
  }
  const { data } = await api.get(`/reports/${date}/characters`, { params: { limit } })
  return data
}

export const fetchReportTags = async (date: string, limit = 20): Promise<PopularTag[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<PopularTag[]>('popular_tags.json')
  }
  const { data } = await api.get(`/reports/${date}/tags`, { params: { limit } })
  return data
}

// ========== 뉴스 API ==========

export interface NewsArticle {
  id: number
  article_id: string
  source: string  // 'naver' | 'google'
  title: string
  description: string | null
  url: string
  publisher: string | null
  published_at: string | null
  crawled_at: string
  keyword: string | null
}

export const fetchNews = async (
  source?: string,
  keyword?: string,
  limit = 50,
  skip = 0
): Promise<NewsArticle[]> => {
  if (USE_STATIC_DATA) {
    // 정적 모드에서는 빈 배열 반환
    return []
  }
  const params: Record<string, any> = { limit, skip }
  if (source) params.source = source
  if (keyword) params.keyword = keyword
  const { data } = await api.get('/news', { params })
  return data
}

export const fetchLatestNews = async (limit = 20): Promise<NewsArticle[]> => {
  if (USE_STATIC_DATA) {
    return []
  }
  const { data } = await api.get('/news/latest', { params: { limit } })
  return data
}

export const fetchNewsSources = async (): Promise<Array<{ source: string; count: number }>> => {
  if (USE_STATIC_DATA) {
    return []
  }
  const { data } = await api.get('/news/sources')
  return data
}

export const triggerNewsCrawl = async (sources?: string[], keywords?: string[]) => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 크롤링을 사용할 수 없습니다.')
  }
  const { data } = await api.post('/news/crawl', { sources, keywords })
  return data
}

export default api
