import { useState, useCallback } from 'react'

const STORAGE_KEY = 'keyword_blocklist'

function loadBlocklist(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveBlocklist(list: string[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

export function useKeywordFilter() {
  const [blocklist, setBlocklist] = useState<string[]>(() => loadBlocklist())

  const addToBlocklist = useCallback((word: string) => {
    setBlocklist(prev => {
      if (prev.includes(word)) return prev
      const next = [...prev, word]
      saveBlocklist(next)
      return next
    })
  }, [])

  const removeFromBlocklist = useCallback((word: string) => {
    setBlocklist(prev => {
      const next = prev.filter(w => w !== word)
      saveBlocklist(next)
      return next
    })
  }, [])

  return { blocklist, addToBlocklist, removeFromBlocklist }
}
