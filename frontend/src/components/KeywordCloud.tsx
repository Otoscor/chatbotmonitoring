interface KeywordItem {
  text: string
  value: number
}

interface KeywordCloudProps {
  keywords: KeywordItem[]
  className?: string
}

export default function KeywordCloud({ keywords, className = '' }: KeywordCloudProps) {
  if (keywords.length === 0) {
    return (
      <div className="keyword-cloud--empty" data-component="keyword-cloud" data-state="empty">
        <p className="text-sm text-gray-400 text-center">키워드 데이터가 없습니다</p>
      </div>
    )
  }

  // 키워드를 값에 따라 크기 조정
  const maxValue = Math.max(...keywords.map(k => k.value))
  const minValue = Math.min(...keywords.map(k => k.value))

  const getFontSize = (value: number) => {
    const normalized = (value - minValue) / (maxValue - minValue || 1)
    return 12 + normalized * 20 // 12px ~ 32px
  }

  return (
    <div className={`keyword-cloud ${className}`} data-component="keyword-cloud">
      <div className="keyword-cloud-container h-full">
        {keywords.map((keyword, index) => (
          <span
            key={index}
            className="keyword-item"
            style={{ fontSize: `${getFontSize(keyword.value)}px` }}
            data-keyword={keyword.text}
          >
            {keyword.text}
          </span>
        ))}
      </div>
    </div>
  )
}
