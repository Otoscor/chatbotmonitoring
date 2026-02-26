/**
 * 저장된 샘플 아코디언 아이템 컴포넌트
 */
import { ChevronDown, ChevronRight, Download, Trash } from '@nsmr/pixelart-react'
import { SavedSample } from '../types'

interface AccordionItemProps {
  sample: SavedSample
  isExpanded: boolean
  onToggle: () => void
  onDelete: () => void
  onDownload: () => void
}

export function AccordionItem({
  sample,
  isExpanded,
  onToggle,
  onDelete,
  onDownload
}: AccordionItemProps) {
  const savedDate = new Date(sample.savedAt).toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })

  return (
    <div className="border border-gray-200 dark:border-gray-800 rounded overflow-hidden">
      {/* 아코디언 헤더 */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-[#1a1a1a] hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-left"
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-500 flex-shrink-0" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500 flex-shrink-0" />
          )}
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {sample.name}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {sample.genre} · {savedDate}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1 flex-shrink-0" onClick={e => e.stopPropagation()}>
          <button
            onClick={onDownload}
            className="p-1.5 text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            title="CSV 다운로드"
          >
            <Download className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onDelete}
            className="p-1.5 text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
            title="삭제"
          >
            <Trash className="w-3.5 h-3.5" />
          </button>
        </div>
      </button>

      {/* 아코디언 내용 */}
      {isExpanded && (
        <div className="p-4 space-y-3 bg-white dark:bg-gray-900 text-sm">
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              작품 제목
            </label>
            <p className="text-gray-800 dark:text-gray-200">{sample.title}</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              작품 소개
            </label>
            <p className="text-gray-600 dark:text-gray-400">{sample.description}</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              캐릭터 프로필
            </label>
            <p className="text-gray-600 dark:text-gray-400">{sample.profile}</p>
          </div>
          {sample.appearancePrompt && (
            <div>
              <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                외모 묘사 <span className="text-[10px] font-normal normal-case">(Midjourney)</span>
              </label>
              <p className="text-gray-600 dark:text-gray-400 font-mono text-xs">{sample.appearancePrompt}</p>
            </div>
          )}
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              시작 메시지
            </label>
            <p className="text-gray-600 dark:text-gray-400 italic">"{sample.openingMessage}"</p>
          </div>
          <div className="flex flex-wrap gap-1 pt-2">
            {sample.hashtags.map((tag, idx) => (
              <span
                key={idx}
                className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
