import { Link, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { triggerCrawl, generateReport, triggerChatServiceCrawl, triggerNewsCrawl, triggerAppReviewCrawl, USE_STATIC_DATA } from '../utils/api'
import { Users, Trophy, Message, Article, Bookmarks, ChartBar, Sun, Moon } from '@nsmr/pixelart-react'
import { useTheme } from '../hooks/useTheme'

interface LayoutProps {
  children: React.ReactNode
}

const navItems = [
  { path: '/', label: '커뮤니티', icon: Users },
  { path: '/character-rankings', label: '캐릭터 순위', icon: Trophy },
  { path: '/app-reviews', label: '리뷰', icon: Message },
  { path: '/news', label: '뉴스', icon: Article },
  { path: '/bookmarks', label: '북마크', icon: Bookmarks },
  { path: '/reports', label: '리포트', icon: ChartBar },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [crawling, setCrawling] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { theme, toggleTheme } = useTheme()

  // Close sidebar on route change
  useEffect(() => {
    setSidebarOpen(false)
  }, [location.pathname])

  // Close sidebar on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSidebarOpen(false)
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [])

  // Prevent body scroll when sidebar is open on mobile
  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [sidebarOpen])

  const handleRefreshAll = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    e.currentTarget.blur()

    if (USE_STATIC_DATA) {
      alert('정적 모드에서는 데이터 갱신을 사용할 수 없습니다.')
      return
    }

    setTimeout(async () => {
      setCrawling(true)

      try {
        await triggerCrawl(undefined, 3)
        await generateReport()
        await triggerChatServiceCrawl(['zeta', 'babechat', 'lunatalk', 'crack', 'caveduck', 'elyn'])
        await triggerAppReviewCrawl()
        await triggerNewsCrawl()
        window.location.reload()
      } catch (error: any) {
        const errorMsg = error.response?.data?.message || error.message || '알 수 없는 오류'
        console.error(`데이터 갱신 중 오류가 발생했습니다: ${errorMsg}`)
        alert(`데이터 갱신 중 오류가 발생했습니다: ${errorMsg}`)
      } finally {
        setCrawling(false)
      }
    }, 50)
  }

  return (
    <div className="app-container">
      {/* Mobile Header */}
      <header className="mobile-header" data-component="mobile-header">
        <button
          type="button"
          onClick={() => setSidebarOpen(true)}
          className="hamburger-button"
          aria-label="메뉴 열기"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <img
          src={theme === 'dark' ? '/logo_dark.png' : '/logo.png'}
          alt="Logo"
          className="h-5 w-auto"
        />
        <button
          type="button"
          onClick={toggleTheme}
          className="theme-toggle-mobile"
          aria-label="테마 변경"
        >
          {theme === 'dark' ? (
            <Moon className="w-5 h-5 force-white-icon" />
          ) : (
            <Sun className="w-5 h-5" />
          )}
        </button>
      </header>

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`app-sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}
        data-component="sidebar"
      >
        {/* Logo */}
        <div className="sidebar-header" data-section="header">
          <img
            src={theme === 'dark' ? '/logo_dark.png' : '/logo.png'}
            alt="Logo"
            className="h-6 w-auto"
          />
          {/* Close button for mobile */}
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="sidebar-close-button"
            aria-label="메뉴 닫기"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav" data-section="navigation">
          <ul className="nav-list">
            {navItems.map(({ path, label, icon: Icon }) => {
              const isActive = location.pathname === path
              return (
                <li key={path}>
                  <Link
                    to={path}
                    className={`
                      nav-item
                      flex items-center gap-[8px]
                      ${isActive ? 'nav-item--active' : ''}
                    `}
                    data-nav-item={path}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <Icon className="w-[18px] h-[18px]" />
                    <span>{label}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Theme Toggle Section */}
        <div className="border-t border-gray-200 dark:border-gray-900 px-3 py-3 shrink-0">
          <button
            type="button"
            onClick={toggleTheme}
            className="
                nav-item
                w-full px-3 py-1.5 rounded transition-colors
                flex items-center gap-[8px]
                dark:text-white
              "
            style={{ fontSize: '13px' }}
            data-action="theme-toggle"
          >
            {theme === 'dark' ? (
              <>
                <span className="force-white-icon flex items-center justify-center">
                  <Moon className="w-[18px] h-[18px]" />
                </span>
                <span className="text-white" style={{ color: '#ffffff' }}>Dark Mode</span>
              </>
            ) : (
              <>
                <Sun className="w-[18px] h-[18px] text-gray-600" />
                <span>Light Mode</span>
              </>
            )}
          </button>
        </div>

        {/* Footer - Data Refresh Button */}
        <div
          className="sidebar-footer p-3 border-t border-gray-200 dark:border-gray-900 shrink-0 flex items-center justify-center"
          data-section="footer"
          style={{ height: '72px', minHeight: '72px' }}
        >
          {!USE_STATIC_DATA && (
            <button
              type="button"
              onClick={handleRefreshAll}
              disabled={crawling}
              className="crawl-button w-full"
              data-action="crawl"
            >
              {crawling ? '크롤링 중...' : '크롤링 시작'}
            </button>
          )}
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
