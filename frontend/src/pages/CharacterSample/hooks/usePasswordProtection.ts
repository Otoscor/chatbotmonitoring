/**
 * 비밀번호 보호 관리 훅
 */
import { useState, useEffect, useRef, useCallback } from 'react'

export function usePasswordProtection() {
  const [showPasswordInput, setShowPasswordInput] = useState(false)
  const [password, setPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [pendingTagPairs, setPendingTagPairs] = useState<string[][] | null>(null)
  const passwordFormRef = useRef<HTMLDivElement>(null)

  // 비밀번호 입력 폼 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        showPasswordInput &&
        passwordFormRef.current &&
        !passwordFormRef.current.contains(event.target as Node)
      ) {
        handleCancel()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showPasswordInput])

  // 비밀번호 입력 모드 활성화
  const requestPassword = useCallback((tagPairs: string[][]): void => {
    setPendingTagPairs(tagPairs)
    setShowPasswordInput(true)
  }, [])

  // 비밀번호 값 지우기
  const clearPassword = useCallback((): void => {
    setPassword('')
    setPasswordError('')
  }, [])

  // 비밀번호 입력 모드 종료
  const handleCancel = useCallback((): void => {
    setShowPasswordInput(false)
    setPassword('')
    setPasswordError('')
    setPendingTagPairs(null)
  }, [])

  // 비밀번호 제출
  const submitPassword = useCallback((): string | null => {
    if (!password.trim()) {
      setPasswordError('비밀번호를 입력해주세요.')
      return null
    }

    const enteredPassword = password
    setShowPasswordInput(false)
    setPassword('')
    setPasswordError('')

    return enteredPassword
  }, [password])

  // 비밀번호 오류 설정
  const setError = useCallback((error: string): void => {
    setPasswordError(error)
    setShowPasswordInput(true)
  }, [])

  // 비밀번호 변경 핸들러
  const handlePasswordChange = useCallback((value: string): void => {
    setPassword(value)
    setPasswordError('')
  }, [])

  return {
    // 상태
    showPasswordInput,
    password,
    passwordError,
    pendingTagPairs,
    passwordFormRef,

    // 액션
    requestPassword,
    clearPassword,
    handleCancel,
    submitPassword,
    setError,
    handlePasswordChange,
    setPendingTagPairs,
  }
}
