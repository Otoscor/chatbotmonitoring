/**
 * 일일 생성 횟수 제한 관리 훅
 */
import { useState, useEffect, useCallback } from 'react'
import { UsageData, DAILY_LIMIT, STORAGE_KEY } from '../types'

function getUsageData(): UsageData {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (!stored) {
    return { count: 0, date: new Date().toDateString() }
  }

  const data: UsageData = JSON.parse(stored)
  const today = new Date().toDateString()

  // 날짜가 바뀌면 카운터 리셋
  if (data.date !== today) {
    return { count: 0, date: today }
  }

  return data
}

function saveUsageData(data: UsageData): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

export function useUsageLimit() {
  const [usageCount, setUsageCount] = useState<number>(0)

  // 컴포넌트 마운트 시 사용 횟수 로드
  useEffect(() => {
    const data = getUsageData()
    setUsageCount(data.count)
  }, [])

  // 사용 횟수 증가
  const incrementUsage = useCallback((): number => {
    const data = getUsageData()
    const newCount = data.count + 1
    saveUsageData({ count: newCount, date: data.date })
    setUsageCount(newCount)
    return newCount
  }, [])

  // 남은 횟수
  const remainingCount = Math.max(0, DAILY_LIMIT - usageCount)
  const isLimitReached = usageCount >= DAILY_LIMIT

  return {
    usageCount,
    remainingCount,
    isLimitReached,
    incrementUsage,
    dailyLimit: DAILY_LIMIT,
  }
}
