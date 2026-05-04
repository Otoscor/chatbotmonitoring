/**
 * 비밀번호 입력 폼 컴포넌트
 */
import { RefObject, FormEvent } from 'react'
import { Lock, Close, Alert } from '@nsmr/pixelart-react'

interface PasswordFormProps {
  password: string
  passwordError: string
  formRef: RefObject<HTMLDivElement>
  onPasswordChange: (value: string) => void
  onClear: () => void
  onSubmit: (e: FormEvent) => void
}

export function PasswordForm({
  password,
  passwordError,
  formRef,
  onPasswordChange,
  onClear,
  onSubmit
}: PasswordFormProps) {
  return (
    <div className="w-full" ref={formRef}>
      <form onSubmit={onSubmit} className="flex items-stretch gap-2">
        {/* 비밀번호 입력 컨테이너 */}
        <div className="flex flex-1 items-center gap-2 h-14 px-6 bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 rounded">
          <Lock className="w-4 h-full text-gray-400 flex-shrink-0" />
          <input
            type="password"
            value={password}
            onChange={(e) => onPasswordChange(e.target.value)}
            placeholder="비밀번호를 입력하세요"
            className="flex-1 h-full bg-transparent text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none text-sm p-3"
            autoFocus
          />
          {password && (
            <button
              type="button"
              onClick={onClear}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors flex-shrink-0 h-full"
              title="지우기"
            >
              <Close className="w-4 h-4" />
            </button>
          )}
        </div>
        {/* 확인 버튼 */}
        <button
          type="submit"
          className="px-6 h-14 bg-white dark:bg-white text-black border border-gray-200 dark:border-gray-800 rounded hover:bg-gray-50 transition-colors font-medium"
        >
          확인
        </button>
      </form>
      {passwordError && (
        <p className="mt-3 text-sm text-red-600 dark:text-red-400 flex items-center justify-center gap-1">
          <Alert className="w-4 h-4" />
          {passwordError}
        </p>
      )}
    </div>
  )
}
