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

  const handleRefreshAll = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation() // 이벤트 버블링 중단
    e.currentTarget.blur() // 버튼 포커스 해제

    if (USE_STATIC_DATA) {
      alert('정적 모드에서는 데이터 갱신을 사용할 수 없습니다.')
      return
    }

    // 렌더링 사이클과 브라우저 팝업 충돌 방지를 위해 약간의 지연 추가
    // 사용자 요청으로 confirm/alert 제거 후 즉시 실행
    setTimeout(async () => {
      setCrawling(true)

      try {
        // 1. 커뮤니티 게시글 크롤링 + 리포트 생성
        await triggerCrawl(undefined, 3)
        await generateReport()

        // 2. 캐릭터챗 서비스 크롤링
        await triggerChatServiceCrawl(['zeta', 'babechat', 'lunatalk', 'crack', 'caveduck', 'elyn'])

        // 3. 뉴스 크롤링
        await triggerNewsCrawl()

        // 완료 알림 없이 바로 새로고침하거나, 토스트 메시지 등을 고려할 수 있음.
        // 여기서는 새로고침만 수행
        window.location.reload()
      } catch (error: any) {
        const errorMsg = error.response?.data?.message || error.message || '알 수 없는 오류'
        // 에러 상황에서는 최소한의 알림이 필요할 수 있으나, 요청에 따라 console.error로 대체하거나 간소화
        console.error(`데이터 갱신 중 오류가 발생했습니다: ${errorMsg}`)
        alert(`데이터 갱신 중 오류가 발생했습니다: ${errorMsg}`) // 에러는 알려주는 게 좋음
      } finally {
        setCrawling(false)
      }
    }, 50)
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="app-sidebar" data-component="sidebar">
        {/* Logo */}
        {/* Logo */}
        <div className="sidebar-header" data-section="header">
          <img src="/logo.png" alt="Logo" className="h-6 w-auto" />
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav" data-section="navigation">
          <ul className="nav-list">
            {navItems.map(({ path, label }) => {
              const isActive = location.pathname === path
              return (
                <li key={path}>
                  <Link
                    to={path}
                    className={`
                      nav-item
                      block px-3 py-1.5 rounded transition-colors
                      ${isActive
                        ? 'bg-gray-200 text-gray-900 font-medium'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }
                    `}
                    data-nav-item={path}
                  >
                    {label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Footer - Data Refresh Button */}
        <div className="sidebar-footer" data-section="footer">
          {!USE_STATIC_DATA && (
            <button
              type="button"
              onClick={handleRefreshAll}
              disabled={crawling}
              className="crawl-button"
              data-action="crawl"
            >
              {crawling ? '크롤링 중...' : '크롤링 시작'}
            </button>
          )}
          <p className="text-xs text-gray-400 text-center mt-3">모니터링 v1.0</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="app-main-content" data-component="main">
        <div className="main-content-wrapper">
          {children}
        </div>
      </main>
    </div>
  )
}
