interface RankingItem {
  rank: number
  name: string
  score: number
}

interface RankingListProps {
  title: string
  items: RankingItem[]
}

export default function RankingList({ title, items }: RankingListProps) {
  return (
    <div className="bg-white border border-gray-200 rounded">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
      </div>
      <div className="divide-y divide-gray-100">
        {items.length === 0 ? (
          <div className="px-4 py-8 text-center text-sm text-gray-400">
            데이터가 없습니다
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.rank}
              className="px-4 py-2.5 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-xs font-medium text-gray-400 w-6">
                  {item.rank}
                </span>
                <span className="text-sm text-gray-900">{item.name}</span>
              </div>
              <span className="text-xs text-gray-500">{item.score.toLocaleString()}</span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
