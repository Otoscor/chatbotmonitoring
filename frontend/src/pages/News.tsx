import { useCallback } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchNews, NewsArticle } from '../utils/api'

export default function News() {
  // 뉴스 데이터 조회 - useApi 훅 사용
  const { data: articles, loading } = useApi(
    useCallback(() => fetchNews(undefined, undefined, 100), [])
  )

  // 날짜 포맷팅
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (hours < 1) return '방금 전'
    if (hours < 24) return `${hours}시간 전`
    if (days < 7) return `${days}일 전`
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
  }




  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div>
        <h1 className="text-xl font-semibold text-gray-900">뉴스</h1>
        <p className="text-sm text-gray-500 mt-1">AI 챗봇/캐릭터 관련 최신 뉴스</p>
      </div>

      {/* 로딩 상태 */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-gray-900"></div>
          <p className="mt-3 text-sm text-gray-500">뉴스를 불러오는 중...</p>
        </div>
      )}

      {/* 빈 상태 */}
      {!loading && (!articles || articles.length === 0) && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-500">뉴스가 없습니다.</p>
          <p className="text-sm text-gray-400 mt-2">사이드바의 "크롤링 시작" 버튼을 클릭하여 뉴스를 수집하세요.</p>
        </div>
      )}

      {/* 뉴스 목록 */}
      {articles && articles.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-gray-500">{articles.length}개의 뉴스</p>

          <div className="grid gap-4">
            {articles.map((article: NewsArticle) => (
              <a
                key={article.id}
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition-all"
              >
                <h3 className="text-sm font-medium text-gray-900 line-clamp-2 leading-snug">
                  {article.title}
                </h3>

                {article.description && (
                  <p className="mt-1.5 text-xs text-gray-500 line-clamp-2">
                    {article.description}
                  </p>
                )}

                <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
                  {article.publisher && (
                    <span>{article.publisher}</span>
                  )}
                  <span>{formatDate(article.published_at)}</span>
                  {article.keyword && (
                    <span className="px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">
                      #{article.keyword}
                    </span>
                  )}
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
