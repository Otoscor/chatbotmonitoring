/**
 * 저장된 샘플 관리 훅
 */
import { useState, useEffect, useCallback } from 'react'
import { GeneratedSample, SavedSample, SAVED_SAMPLES_KEY } from '../types'

function getSavedSamplesFromStorage(): SavedSample[] {
  const stored = localStorage.getItem(SAVED_SAMPLES_KEY)
  if (!stored) return []
  try {
    return JSON.parse(stored)
  } catch {
    return []
  }
}

function saveSamplesToStorage(samples: SavedSample[]): void {
  localStorage.setItem(SAVED_SAMPLES_KEY, JSON.stringify(samples))
}

export function useSavedSamples() {
  const [savedSamples, setSavedSamples] = useState<SavedSample[]>([])
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  // 컴포넌트 마운트 시 저장된 샘플 로드
  useEffect(() => {
    setSavedSamples(getSavedSamplesFromStorage())
  }, [])

  // 샘플 저장
  const saveSample = useCallback((sample: GeneratedSample): SavedSample => {
    const savedSample: SavedSample = {
      ...sample,
      savedAt: new Date().toISOString(),
      savedId: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }

    setSavedSamples(prev => {
      const updated = [savedSample, ...prev]
      saveSamplesToStorage(updated)
      return updated
    })

    return savedSample
  }, [])

  // 저장된 샘플 삭제
  const removeSample = useCallback((savedId: string): void => {
    setSavedSamples(prev => {
      const filtered = prev.filter(s => s.savedId !== savedId)
      saveSamplesToStorage(filtered)
      return filtered
    })

    setExpandedIds(prev => {
      const next = new Set(prev)
      next.delete(savedId)
      return next
    })
  }, [])

  // 아코디언 토글
  const toggleExpand = useCallback((savedId: string): void => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      if (next.has(savedId)) {
        next.delete(savedId)
      } else {
        next.add(savedId)
      }
      return next
    })
  }, [])

  // 확장 상태 확인
  const isExpanded = useCallback((savedId: string): boolean => {
    return expandedIds.has(savedId)
  }, [expandedIds])

  return {
    savedSamples,
    saveSample,
    removeSample,
    toggleExpand,
    isExpanded,
  }
}
