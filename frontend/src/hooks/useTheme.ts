import { useEffect, useState } from 'react'

type Theme = 'light' | 'dark'

export function useTheme() {
    const [theme, setTheme] = useState<Theme>(() => {
        // localStorage에서 저장된 테마 확인
        const savedTheme = localStorage.getItem('theme') as Theme | null

        if (savedTheme) {
            return savedTheme
        }

        // 시스템 설정 확인
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark'
        }

        // 기본값은 light
        return 'light'
    })

    useEffect(() => {
        const root = document.documentElement

        // 이전 클래스 제거
        root.classList.remove('light', 'dark')

        // 현재 테마 클래스 추가
        root.classList.add(theme)

        // localStorage에 저장
        localStorage.setItem('theme', theme)
    }, [theme])

    const toggleTheme = () => {
        setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'))
    }

    return { theme, toggleTheme }
}
