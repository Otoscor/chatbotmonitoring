/**
 * 인기 태그 조합 TOP 10 컴포넌트
 */
import { TagCooccurrence } from '../types'

interface TagCombinationsProps {
  combinations: TagCooccurrence[]
}

export function TagCombinations({ combinations }: TagCombinationsProps) {
  return (
    <section className="card p-6" data-section="popular-combinations">
      <h3 className="section-title mb-4">인기 태그 조합 TOP 10</h3>
      <div className="flex flex-wrap gap-2">
        {combinations.map((combo, idx) => (
          <div
            key={idx}
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-gray-100 dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-800 rounded text-sm"
          >
            <span className="text-gray-500 dark:text-gray-400 text-xs mr-1">
              {idx + 1}.
            </span>
            <span className="font-medium text-gray-800 dark:text-gray-200">
              #{combo.tag1}
            </span>
            <span className="text-gray-400">+</span>
            <span className="font-medium text-gray-800 dark:text-gray-200">
              #{combo.tag2}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">
              ({combo.count}회)
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}
