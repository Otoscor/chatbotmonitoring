import { useCallback } from 'react'
import RankingList from '../components/RankingList'
import { useApi } from '../hooks/useApi'
import { fetchTrendingKeywords } from '../utils/api'

export default function Characters() {
  const { data: ranking, loading } = useApi(
    useCallback(() => fetchTrendingKeywords(7, 50), [])
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-sm text-gray-400">데이터를 불러오는 중...</div>
      </div>
    )
  }

  const rankingItems = ranking?.map((k: any, idx: number) => ({
    rank: idx + 1,
    name: k.keyword,
    score: k.total_count
  })) || []

  return (
    <div className="space-y-6">
      <div className="pb-6 border-b border-gray-200">
        <h1 className="text-2xl font-semibold text-gray-900 mb-1">키워드 순위</h1>
        <p className="text-sm text-gray-500">인기 키워드 랭킹을 확인하세요</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <RankingList
          title="TOP 25"
          items={rankingItems.slice(0, 25)}
        />
        <RankingList
          title="26-50위"
          items={rankingItems.slice(25, 50)}
        />
      </div>
    </div>
  )
}
