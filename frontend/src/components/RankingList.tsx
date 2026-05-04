interface RankingItem {
  rank: number
  name: string
  score: number
}

interface RankingListProps {
  title: string
  items: RankingItem[]
  className?: string
}

export default function RankingList({ title, items, className = '' }: RankingListProps) {
  return (
    <div className={`ranking-list flex flex-col ${className}`} data-component="ranking-list">
      <div className="ranking-list-header">
        <h3 className="ranking-list-title">{title}</h3>
      </div>
      <div className="ranking-list-body flex-1 overflow-y-auto min-h-0">
        {items.length === 0 ? (
          <div className="px-4 py-8 text-center text-sm text-gray-400" data-state="empty">
            데이터가 없습니다
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.rank}
              className="ranking-list-item"
              data-rank={item.rank}
            >
              <div className="flex items-center gap-3">
                <span className="ranking-position">
                  {item.rank}
                </span>
                <span className="ranking-name">{item.name}</span>
              </div>
              <span className="ranking-score">{item.score.toLocaleString()}</span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
