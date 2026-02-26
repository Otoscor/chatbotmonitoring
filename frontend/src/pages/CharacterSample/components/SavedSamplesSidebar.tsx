/**
 * 저장된 샘플 사이드바 컴포넌트
 */
import { Folder, Close } from '@nsmr/pixelart-react'
import { SavedSample } from '../types'
import { AccordionItem } from './AccordionItem'

interface SavedSamplesSidebarProps {
  samples: SavedSample[]
  isExpanded: (id: string) => boolean
  onToggle: (id: string) => void
  onDelete: (id: string) => void
  onDownload: (sample: SavedSample) => void
  // 모바일용
  isMobileOpen?: boolean
  onMobileClose?: () => void
}

export function SavedSamplesSidebar({
  samples,
  isExpanded,
  onToggle,
  onDelete,
  onDownload,
  isMobileOpen = false,
  onMobileClose
}: SavedSamplesSidebarProps) {
  const EmptyState = () => (
    <div className="text-center py-8 text-sm text-gray-500 dark:text-gray-400">
      <Folder className="w-8 h-8 mx-auto mb-2 opacity-30" />
      <p>저장된 샘플이 없습니다.</p>
      <p className="text-xs mt-1">캐릭터 생성 후 저장해보세요!</p>
    </div>
  )

  const SampleList = () => (
    <div className="space-y-2">
      {samples.map(sample => (
        <AccordionItem
          key={sample.savedId}
          sample={sample}
          isExpanded={isExpanded(sample.savedId)}
          onToggle={() => onToggle(sample.savedId)}
          onDelete={() => onDelete(sample.savedId)}
          onDownload={() => onDownload(sample)}
        />
      ))}
    </div>
  )

  return (
    <>
      {/* 데스크탑: 오른쪽 사이드바 */}
      <aside className="hidden lg:block w-80 ml-6 flex-shrink-0">
        <div className="sticky top-6">
          <div className="card p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Folder className="w-4 h-4" />
                저장된 샘플
              </h3>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {samples.length}개
              </span>
            </div>

            {samples.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="max-h-[calc(100vh-200px)] overflow-y-auto">
                <SampleList />
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* 모바일: 바텀시트 오버레이 */}
      {isMobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          {/* 배경 오버레이 */}
          <div
            className="absolute inset-0 bg-black/50"
            onClick={onMobileClose}
          />

          {/* 바텀시트 */}
          <div className="absolute bottom-0 left-0 right-0 bg-white dark:bg-gray-900 rounded-t-2xl shadow-xl max-h-[80vh] flex flex-col animate-slide-up">
            {/* 핸들 바 */}
            <div className="flex justify-center py-3">
              <div className="w-12 h-1.5 bg-gray-300 dark:bg-gray-600 rounded-full" />
            </div>

            {/* 헤더 */}
            <div className="flex items-center justify-between px-4 pb-3 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <Folder className="w-4 h-4" />
                저장된 샘플
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ({samples.length}개)
                </span>
              </h3>
              <button
                onClick={onMobileClose}
                className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <Close className="w-5 h-5" />
              </button>
            </div>

            {/* 콘텐츠 */}
            <div className="flex-1 overflow-y-auto p-4">
              {samples.length === 0 ? <EmptyState /> : <SampleList />}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
