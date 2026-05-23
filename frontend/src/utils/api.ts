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

// API 파라미터 타입 정의
interface PopularPostsParams {
  limit: number
  days: number
  gallery_id?: string
}

interface ChatCharactersParams {
  limit: number
  service?: string
}

interface PopularTagsParams {
  limit: number
  service?: string
}

interface NewsParams {
  limit: number
  skip: number
  source?: string
  keyword?: string
}

interface BookmarksParams {
  skip: number
  limit: number
  category?: string
}

interface AppReviewsParams {
  limit: number
  app_name?: string
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

export interface Bookmark {
  id: number
  url: string
  title?: string
  description?: string
  ai_summary?: string
  thumbnail_url?: string
  site_name?: string
  category: string
  tags?: string[]
  user_note?: string
  is_summarized: number  // 0: 대기, 1: 완료, 2: 실패
  created_at: string
  updated_at: string
}

export interface KeywordTrend {
  keyword: string
  total_count: number
  rank: number
  sentiment_score?: number // -1.0 to 1.0
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
    const allPosts = await fetchStaticData<Post[]>('popular_posts.json')
    if (galleryId) {
      return allPosts.filter(post => post.gallery_id === galleryId).slice(0, limit)
    }
    return allPosts.slice(0, limit)
  }
  const params: PopularPostsParams = { limit, days }
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
  const { data } = await api.post('/crawl', { gallery_id: galleryId, pages }, { timeout: 0 })
  return data
}

export const generateReport = async (date?: string) => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 리포트 생성을 사용할 수 없습니다.')
  }
  const { data } = await api.post('/reports/generate', null, { params: { date }, timeout: 0 })
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
  const params: ChatCharactersParams = { limit }
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
  const { data } = await api.post('/characters/crawl-chat-services', { services }, { timeout: 0 })
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
  const params: PopularTagsParams = { limit }
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
    const allNews = await fetchStaticData<NewsArticle[]>('news.json')
    let filtered = allNews

    // 필터링
    if (source) {
      filtered = filtered.filter(n => n.source === source)
    }
    if (keyword) {
      const lowerKeyword = keyword.toLowerCase()
      filtered = filtered.filter(n =>
        n.title.toLowerCase().includes(lowerKeyword) ||
        (n.description && n.description.toLowerCase().includes(lowerKeyword)) ||
        (n.keyword && n.keyword.toLowerCase().includes(lowerKeyword))
      )
    }

    // 페이지네이션
    return filtered.slice(skip, skip + limit)
  }
  const params: NewsParams = { limit, skip }
  if (source) params.source = source
  if (keyword) params.keyword = keyword
  const { data } = await api.get('/news', { params })
  return data
}

export const fetchLatestNews = async (limit = 20): Promise<NewsArticle[]> => {
  if (USE_STATIC_DATA) {
    const allNews = await fetchStaticData<NewsArticle[]>('news.json')
    return allNews.slice(0, limit)
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
  const { data } = await api.post('/news/crawl', { sources, keywords }, { timeout: 0 })
  return data
}

// ========== 북마크 API ==========

export const addBookmark = async (url: string, category = 'post'): Promise<Bookmark> => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 북마크를 추가할 수 없습니다.')
  }
  const { data } = await api.post('/bookmarks', { url, category })
  return data
}

// 북마크 목록 조회
export const fetchBookmarks = async (skip = 0, limit = 50, category?: string) => {
  if (USE_STATIC_DATA) {
    const allBookmarks = await fetchStaticData<Bookmark[]>('bookmarks.json')
    let filtered = allBookmarks
    // 정적 모드 카테고리 필터링
    if (category) {
      filtered = allBookmarks.filter(b => b.category === category)
    }
    return filtered.slice(skip, skip + limit)
  }
  const params: BookmarksParams = { skip, limit }
  if (category) {
    params.category = category
  }
  const { data } = await api.get('/bookmarks', { params })
  return data
}

export const fetchBookmark = async (id: number): Promise<Bookmark> => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 북마크를 조회할 수 없습니다.')
  }
  const { data } = await api.get(`/bookmarks/${id}`)
  return data
}

export const updateBookmark = async (id: number, updates: { tags?: string[]; user_note?: string }): Promise<Bookmark> => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 북마크를 수정할 수 없습니다.')
  }
  const { data } = await api.put(`/bookmarks/${id}`, updates)
  return data
}

export const deleteBookmark = async (id: number): Promise<void> => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 북마크를 삭제할 수 없습니다.')
  }
  await api.delete(`/bookmarks/${id}`)
}

export const resummaryBookmark = async (id: number): Promise<Bookmark> => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 요약을 재생성할 수 없습니다.')
  }
  const { data } = await api.post(`/bookmarks/${id}/summarize`)
  return data
}

// ========== 앱 리뷰 API ==========
export interface AppReview {
  id: number
  app_name: string
  platform: string
  review_text: string | null
  rating: number
  reviewer_name: string | null
  review_date: string | null
}

export interface AppStats {
  app_name: string
  total_reviews: number
  average_rating: number
  rating_distribution: { [key: number]: number }
  platform_distribution: { [key: string]: number }
}

export const fetchAppStats = async (): Promise<AppStats[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<AppStats[]>('app_stats.json')
  }
  const { data } = await api.get('/app-reviews/stats')
  return data
}

export const fetchAppReviews = async (appName?: string, limit = 100): Promise<AppReview[]> => {
  if (USE_STATIC_DATA) {
    const allReviews = await fetchStaticData<AppReview[]>('app_reviews.json')
    // 정적 모드 필터링
    if (appName) {
      return allReviews.filter(r => r.app_name === appName).slice(0, limit)
    }
    return allReviews.slice(0, limit)
  }
  const params: AppReviewsParams = { limit }
  if (appName) params.app_name = appName
  const { data } = await api.get('/app-reviews', { params })
  return data
}

export const fetchAppKeywords = async (appName?: string, limit = 20): Promise<KeywordTrend[]> => {
  if (USE_STATIC_DATA) {
    return fetchStaticData<KeywordTrend[]>('app_keywords.json')
  }
  const params: AppReviewsParams = { limit }
  if (appName) params.app_name = appName
  const { data } = await api.get('/app-reviews/keywords', { params })
  return data
}

export const triggerAppReviewCrawl = async () => {
  if (USE_STATIC_DATA) {
    throw new Error('정적 모드에서는 앱 리뷰 크롤링을 사용할 수 없습니다.')
  }
  const { data } = await api.post('/app-reviews/crawl', null, { timeout: 0 })
  return data
}

export const fetchTodayReviews = async (): Promise<AppReview[]> => {
  if (USE_STATIC_DATA) {
    try {
      return await fetchStaticData<AppReview[]>('today_reviews.json')
    } catch {
      return []
    }
  }
  const { data } = await api.get('/app-reviews/today')
  return data
}

// ========== 캐릭터 샘플 API ==========
export interface CharacterSample {
  id: number
  title: string              // 작품 제목
  description: string        // 작품 소개글
  name: string               // 캐릭터명
  profile: string            // 캐릭터 프로필 (외모+성격+말투)
  appearancePrompt?: string  // 미드저니용 외모 묘사 프롬프트 (영어)
  backgroundIntro: string    // 배경 소개글
  worldPrompt: string        // 세계관 프롬프트
  firstDaySituation: string  // 첫날 상황
  openingMessage: string     // 시작 메시지
  genre: string              // 대표 장르
  hashtags: string[]         // 해시태그
  tags: string[]             // 기존 태그 (호환용)
  basedOn: string[]          // 참고 캐릭터
}

// 비밀번호 필요 여부 에러
export class PasswordRequiredError extends Error {
  constructor(message: string = '비밀번호가 필요합니다.') {
    super(message)
    this.name = 'PasswordRequiredError'
  }
}

export const generateCharacterSamples = async (
  tagCombinations: string[][],
  password?: string
): Promise<CharacterSample[]> => {
  // 정적 모드(Vercel 배포)에서는 Vercel Serverless Function 사용
  if (USE_STATIC_DATA) {
    const response = await fetch('/api/generate-character', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tag_combinations: tagCombinations, password })
    })

    // 응답 텍스트 먼저 확인
    const responseText = await response.text()
    console.log('Serverless function response:', responseText)

    if (!response.ok) {
      let errorMessage = '캐릭터 샘플 생성에 실패했습니다.'
      try {
        const error = JSON.parse(responseText)
        errorMessage = error.error || errorMessage
        // 401 에러이고 비밀번호가 필요한 경우
        if (response.status === 401 && error.requirePassword) {
          throw new PasswordRequiredError(errorMessage)
        }
      } catch (e) {
        if (e instanceof PasswordRequiredError) throw e
        errorMessage = responseText || errorMessage
      }
      throw new Error(errorMessage)
    }

    try {
      const data = JSON.parse(responseText)
      return data.samples
    } catch (e) {
      console.error('JSON parse error:', e, 'Response:', responseText)
      throw new Error('서버 응답을 파싱할 수 없습니다.')
    }
  }

  // 로컬 개발 환경에서는 백엔드 API 사용
  const { data } = await api.post('/character-samples/generate', {
    tag_combinations: tagCombinations
  })
  return data.samples
}

export default api
