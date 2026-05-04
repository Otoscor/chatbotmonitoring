/**
 * 샘플 생성 버튼 컴포넌트
 */
import { Reload, Alert } from '@nsmr/pixelart-react'

interface GenerateButtonProps {
  generating: boolean
  disabled: boolean
  isLimitReached: boolean
  error: string
  remainingCount: number
  dailyLimit: number
  onClick: () => void
}

export function GenerateButton({
  generating,
  disabled,
  isLimitReached,
  error,
  remainingCount,
  dailyLimit,
  onClick
}: GenerateButtonProps) {
  return (
    <>
      {/* 생성 버튼 */}
      <button
        onClick={onClick}
        disabled={disabled}
        className="w-full flex items-center justify-center gap-2 h-14 px-6 bg-black text-white border border-gray-200 dark:border-gray-800 rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        data-action="generate"
      >
        <Reload className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
        {generating
          ? 'Gemini AI 생성 중...'
          : isLimitReached
            ? '오늘의 생성 횟수 초과'
            : '캐릭터 샘플 생성'}
      </button>

      {/* 에러 메시지 */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 px-4 py-2 rounded">
          <Alert className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* 남은 횟수 표시 */}
      <div className="text-sm text-gray-600 dark:text-gray-400">
        {isLimitReached ? (
          <span className="text-red-500 dark:text-red-400 font-medium">
            오늘의 생성 횟수를 모두 사용했습니다. 내일 다시 시도해주세요.
          </span>
        ) : (
          <>
            오늘 남은 생성 횟수: <span className="font-semibold text-gray-900 dark:text-white">{remainingCount}</span>회 / {dailyLimit}회
          </>
        )}
      </div>
    </>
  )
}
