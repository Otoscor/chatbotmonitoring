import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { triggerCrawl, generateReport, triggerChatServiceCrawl, triggerNewsCrawl, USE_STATIC_DATA } from '../utils/api'

interface LayoutProps {
  children: React.ReactNode
}

const navItems = [
  { path: '/', label: '커뮤니티' },
  { path: '/character-rankings', label: '캐릭터 순위' },
  { path: '/app-reviews', label: '리뷰' },
  { path: '/news', label: '뉴스' },
  { path: '/bookmarks', label: '북마크' },
  { path: '/reports', label: '리포트' },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [crawling, setCrawling] = useState(false)

  const handleRefreshAll = async () => {
    if (USE_STATIC_DATA) {
      alert('정적 모드에서는 데이터 갱신을 사용할 수 없습니다.')
      return
    }

    const isConfirmed = window.confirm(
      '모든 데이터를 크롤링하시겠습니까?\n' +
      '• 커뮤니티 게시글\n' +
      '• 캐릭터챗 서비스\n' +
      '• 뉴스 기사\n' +
      '• 리포트 생성\n\n' +
      '(약 1-2분 소요)'
    )
    if (!isConfirmed) return

    setCrawling(true)

    try {
      alert('데이터 갱신을 시작합니다. 잠시만 기다려주세요...')

      // 1. 커뮤니티 게시글 크롤링 + 리포트 생성
      await triggerCrawl(undefined, 3)
      await generateReport()

      // 2. 캐릭터챗 서비스 크롤링
      await triggerChatServiceCrawl(['zeta', 'babechat', 'lunatalk', 'crack'])

      // 3. 뉴스 크롤링
      await triggerNewsCrawl()

      alert('모든 데이터 갱신이 완료되었습니다!')
      window.location.reload()
    } catch (error: any) {
      const errorMsg = error.response?.data?.message || error.message || '알 수 없는 오류'
      alert(`데이터 갱신 중 오류가 발생했습니다: ${errorMsg}`)
      console.error(error)
    } finally {
      setCrawling(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-white">
      {/* Sidebar */}
      <aside className="fixed top-0 left-0 h-screen w-60 bg-gray-50 border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-gray-200">
          <h1 className="text-sm font-semibold text-gray-900">챗봇 모니터링</h1>
          <p className="text-xs text-gray-500 mt-0.5">캐릭터 챗을 이해하기 위한 모니터링</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-3">
          <ul className="space-y-0.5">
            {navItems.map(({ path, label }) => {
              const isActive = location.pathname === path
              return (
                <li key={path}>
                  <Link
                    to={path}
                    className={`
                      block px-3 py-1.5 rounded text-sm transition-colors
                      ${isActive
                        ? 'bg-gray-200 text-gray-900 font-medium'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }
                    `}
                  >
                    {label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Footer - Data Refresh Button */}
        <div className="px-3 py-3 border-t border-gray-200">
          {!USE_STATIC_DATA && (
            <button
              onClick={handleRefreshAll}
              disabled={crawling}
              className="w-full px-3 py-2 text-sm font-medium bg-gray-900 text-white rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {crawling ? '크롤링 중...' : '크롤링 시작'}
            </button>
          )}
          <p className="text-xs text-gray-400 text-center mt-3">모니터링 v1.0</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto ml-60">
        <div className="max-w-6xl mx-auto px-12 py-10">
          {children}
        </div>
      </main>
    </div>
  )
}
