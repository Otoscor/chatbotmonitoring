import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface LayoutProps {
  children: ReactNode
}

const navItems = [
  { path: '/', label: '대시보드' },
  { path: '/character-rankings', label: '캐릭터 순위' },
  { path: '/reports', label: '리포트' },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen flex bg-white">
      {/* Sidebar */}
      <aside className="fixed top-0 left-0 h-screen w-60 bg-gray-50 border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-gray-200">
          <h1 className="text-sm font-semibold text-gray-900">모니터링 시스템</h1>
          <p className="text-xs text-gray-500 mt-0.5">캐릭터 챗봇 분석</p>
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

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200">
          <p className="text-xs text-gray-400">모니터링 v1.0</p>
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
