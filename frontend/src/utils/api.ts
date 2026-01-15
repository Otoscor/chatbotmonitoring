import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2분으로 증가
  headers: {
    'Content-Type': 'application/json',
  },
})

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
  const { data } = await api.get('/posts', { params: { skip, limit } })
  return data
}

export const fetchPopularPosts = async (limit = 15, days = 7): Promise<Post[]> => {
  const { data } = await api.get('/posts/popular', { params: { limit, days } })
  return data
}

export const fetchDailyStats = async (date?: string): Promise<Stats> => {
  const { data } = await api.get('/posts/stats/daily', { params: { date } })
  return data
}

export const fetchReports = async (skip = 0, limit = 30): Promise<DailyReport[]> => {
  const { data } = await api.get('/reports', { params: { skip, limit } })
  return data
}

export const fetchLatestReport = async (): Promise<DailyReport> => {
  const { data } = await api.get('/reports/latest')
  return data
}

export const fetchReportByDate = async (date: string): Promise<DailyReport> => {
  const { data } = await api.get(`/reports/${date}`)
  return data
}

export const fetchTrendingKeywords = async (days = 7, limit = 20): Promise<KeywordTrend[]> => {
  const { data } = await api.get('/keywords/trending', { params: { days, limit } })
  return data
}

export const fetchCharacterRanking = async (days = 7, limit = 20): Promise<CharacterRanking[]> => {
  const { data } = await api.get('/characters/ranking', { params: { days, limit } })
  return data
}

export const triggerCrawl = async (galleryId?: string, pages = 5) => {
  const { data } = await api.post('/crawl', { gallery_id: galleryId, pages })
  return data
}

export const generateReport = async (date?: string) => {
  const { data } = await api.post('/reports/generate', null, { params: { date } })
  return data
}

export const fetchChatServiceCharacters = async (service?: string, limit = 30): Promise<ChatServiceCharacter[]> => {
  const params: any = { limit }
  if (service) {
    params.service = service
  }
  const { data } = await api.get('/characters/chat-services', { params })
  return data
}

export const triggerChatServiceCrawl = async (services?: string[]) => {
  const { data } = await api.post('/characters/crawl-chat-services', { services })
  return data
}

export default api
