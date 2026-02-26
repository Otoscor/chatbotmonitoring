/**
 * 생성된 샘플 카드 컴포넌트
 */
import { Download, Save } from '@nsmr/pixelart-react'
import { GeneratedSample } from '../types'

interface GeneratedSampleCardProps {
  sample: GeneratedSample
  onSave: (sample: GeneratedSample) => void
  onDownload: (sample: GeneratedSample) => void
}

export function GeneratedSampleCard({ sample, onSave, onDownload }: GeneratedSampleCardProps) {
  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(sample.appearancePrompt)
  }

  return (
    <div
      className="card p-6 space-y-5"
      data-sample-id={sample.id}
    >
      {/* 헤더: 작품 제목 + 장르 + 태그 */}
      <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs font-medium rounded">
            {sample.genre}
          </span>
        </div>
        <h4 className="font-bold text-gray-900 dark:text-white text-lg mb-2">
          {sample.title}
        </h4>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          {sample.description}
        </p>
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex flex-wrap gap-1">
            {sample.hashtags.map((tag, idx) => (
              <span
                key={idx}
                className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded"
              >
                #{tag}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onSave(sample)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600 rounded transition-colors whitespace-nowrap"
              title="저장하기"
            >
              <Save className="w-3.5 h-3.5" />
              저장
            </button>
            <button
              onClick={() => onDownload(sample)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-[#0a0a0a] border border-gray-300 dark:border-gray-700 rounded hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors whitespace-nowrap"
              title="CSV로 추출"
            >
              <Download className="w-3.5 h-3.5" />
              CSV
            </button>
          </div>
        </div>
      </div>

      {/* 캐릭터 정보 */}
      <div className="space-y-4">
        <SampleField label="캐릭터 이름" value={sample.name} />
        <SampleField label="캐릭터 프로필" value={sample.profile} />

        {sample.appearancePrompt && (
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              외모 묘사 <span className="text-[10px] font-normal normal-case">(Midjourney Prompt)</span>
            </label>
            <div className="relative">
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 p-3 rounded font-mono">
                {sample.appearancePrompt}
              </p>
              <button
                type="button"
                onClick={handleCopyPrompt}
                className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                title="복사"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
          </div>
        )}

        <SampleField label="배경 소개글" value={sample.backgroundIntro} />
        <SampleField label="세계관 프롬프트" value={sample.worldPrompt} />
        <SampleField label="첫날 상황" value={sample.firstDaySituation} />
        <SampleField label="시작 메시지" value={`"${sample.openingMessage}"`} />
      </div>

      {/* 참고 캐릭터 */}
      {sample.basedOn && sample.basedOn.length > 0 && (
        <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
          <span className="text-xs text-gray-500 dark:text-gray-500">
            참고 캐릭터: {sample.basedOn.join(', ')}
          </span>
        </div>
      )}
    </div>
  )
}

// 필드 표시 헬퍼 컴포넌트
function SampleField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
        {label}
      </label>
      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 p-3 rounded">
        {value}
      </p>
    </div>
  )
}
