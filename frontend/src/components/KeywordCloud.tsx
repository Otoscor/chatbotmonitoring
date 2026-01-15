interface KeywordItem {
  text: string
  value: number
}

interface KeywordCloudProps {
  keywords: KeywordItem[]
}

export default function KeywordCloud({ keywords }: KeywordCloudProps) {
  if (keywords.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded p-8">
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
    <div className="bg-white border border-gray-200 rounded p-6">
      <div className="flex flex-wrap gap-3 items-center justify-center">
        {keywords.map((keyword, index) => (
          <span
            key={index}
            className="text-gray-700 hover:text-gray-900 transition-colors cursor-default"
            style={{ fontSize: `${getFontSize(keyword.value)}px` }}
          >
            {keyword.text}
          </span>
        ))}
      </div>
    </div>
  )
}
