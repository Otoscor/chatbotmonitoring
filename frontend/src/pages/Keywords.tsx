import { useCallback } from 'react'
import KeywordCloud from '../components/KeywordCloud'
import { useApi } from '../hooks/useApi'
import { useKeywordFilter } from '../hooks/useKeywordFilter'
import { fetchLatestReport } from '../utils/api'

export default function Keywords() {
  const { data: report, loading } = useApi(
    useCallback(() => fetchLatestReport(), [])
  )
  const { blocklist, addToBlocklist, removeFromBlocklist } = useKeywordFilter()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-sm text-gray-400">데이터를 불러오는 중...</div>
      </div>
    )
  }

  const allKeywords = report?.top_keywords?.map((k: any) => ({
    text: k.keyword,
    value: k.count
  })) || []

  const filteredKeywords = allKeywords.filter(k => !blocklist.includes(k.text))

  return (
    <div className="space-y-6">
      <div className="pb-6 border-b border-gray-200">
        <h1 className="page-title">키워드 분석</h1>
        <p className="text-sm text-gray-500">주요 키워드 트렌드를 확인하세요</p>
      </div>

      {/* 블록리스트 관리 */}
      {blocklist.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded p-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            숨긴 키워드
          </h3>
          <div className="flex flex-wrap gap-2">
            {blocklist.map(word => (
              <span
                key={word}
                className="inline-flex items-center gap-1 px-2 py-1 bg-white border border-gray-300 rounded text-xs text-gray-600"
              >
                {word}
                <button
                  onClick={() => removeFromBlocklist(word)}
                  className="text-gray-400 hover:text-gray-700 transition-colors ml-0.5"
                  title="숨기기 해제"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-3">인기 키워드</h3>
        <KeywordCloud keywords={filteredKeywords} />
      </div>

      <div className="bg-white border border-gray-200 rounded">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900">키워드 목록</h3>
        </div>
        <div className="divide-y divide-gray-100">
          {allKeywords.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-gray-400">
              키워드 데이터가 없습니다
            </div>
          ) : (
            allKeywords
              .sort((a, b) => b.value - a.value)
              .map((keyword, idx) => {
                const isBlocked = blocklist.includes(keyword.text)
                return (
                  <div
                    key={idx}
                    className={`px-4 py-2.5 flex items-center justify-between hover:bg-gray-50 transition-colors ${isBlocked ? 'opacity-40' : ''}`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-medium text-gray-400 w-6">
                        {idx + 1}
                      </span>
                      <span className="text-sm text-gray-900">{keyword.text}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-500">{keyword.value.toLocaleString()}</span>
                      <button
                        onClick={() => isBlocked ? removeFromBlocklist(keyword.text) : addToBlocklist(keyword.text)}
                        className={`text-sm transition-colors ${isBlocked ? 'text-gray-400 hover:text-gray-700' : 'text-gray-300 hover:text-red-500'}`}
                        title={isBlocked ? '숨기기 해제' : '이 키워드 숨기기'}
                      >
                        {isBlocked ? '↩' : '🚫'}
                      </button>
                    </div>
                  </div>
                )
              })
          )}
        </div>
      </div>
    </div>
  )
}
