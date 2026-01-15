import { useCallback } from 'react'
import KeywordCloud from '../components/KeywordCloud'
import { useApi } from '../hooks/useApi'
import { fetchLatestReport } from '../utils/api'

export default function Keywords() {
  const { data: report, loading } = useApi(
    useCallback(() => fetchLatestReport(), [])
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-sm text-gray-400">데이터를 불러오는 중...</div>
      </div>
    )
  }

  const keywords = report?.top_keywords?.map((k: any) => ({
    text: k.keyword,
    value: k.count
  })) || []

  return (
    <div className="space-y-6">
      <div className="pb-6 border-b border-gray-200">
        <h1 className="text-2xl font-semibold text-gray-900 mb-1">키워드 분석</h1>
        <p className="text-sm text-gray-500">주요 키워드 트렌드를 확인하세요</p>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-3">인기 키워드</h3>
        <KeywordCloud keywords={keywords} />
      </div>

      <div className="bg-white border border-gray-200 rounded">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900">키워드 목록</h3>
        </div>
        <div className="divide-y divide-gray-100">
          {keywords.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-gray-400">
              키워드 데이터가 없습니다
            </div>
          ) : (
            keywords
              .sort((a, b) => b.value - a.value)
              .map((keyword, idx) => (
                <div
                  key={idx}
                  className="px-4 py-2.5 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-medium text-gray-400 w-6">
                      {idx + 1}
                    </span>
                    <span className="text-sm text-gray-900">{keyword.text}</span>
                  </div>
                  <span className="text-xs text-gray-500">{keyword.value.toLocaleString()}</span>
                </div>
              ))
          )}
        </div>
      </div>
    </div>
  )
}
