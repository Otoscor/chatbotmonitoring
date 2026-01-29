import { useCallback, useState, useEffect } from 'react'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

import StatCard from '../components/StatCard'
import KeywordCloud from '../components/KeywordCloud'
import RankingList from '../components/RankingList'
import { useApi } from '../hooks/useApi'
import {
  fetchLatestReport,
  fetchReports,
  fetchPopularPosts,
  type DailyReport,
  type Post
} from '../utils/api'

// 갤러리 탭 정의
const GALLERY_TABS = [
  { id: 'all', label: '전체', galleryId: undefined },
  { id: 'wrtnai', label: '뤼튼 마이너갤', galleryId: 'wrtnai' },
  { id: 'aichatting', label: 'AI챗팅 마이너갤', galleryId: 'aichatting' },
  { id: 'characterai', label: '아카라이브 캐릭터AI', galleryId: 'characterai' },
]

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('all')
  const [popularPosts, setPopularPosts] = useState<Post[]>([])
  const [postsLoading, setPostsLoading] = useState(false)

  const { data: latestReport, loading: reportLoading } = useApi(
    useCallback(() => fetchLatestReport(), [])
  )

  const { data: reports } = useApi(
    useCallback(() => fetchReports(0, 7), [])
  )

  const currentGalleryId = GALLERY_TABS.find(tab => tab.id === activeTab)?.galleryId

  // 탭 변경 시 게시글 다시 가져오기
  useEffect(() => {
    const loadPosts = async () => {
      setPostsLoading(true)
      try {
        const data = await fetchPopularPosts(15, 7, currentGalleryId)
        setPopularPosts(data)
      } catch (error) {
        console.error("Failed to fetch popular posts:", error)
        setPopularPosts([])
      } finally {
        setPostsLoading(false)
      }
    }

    loadPosts()
  }, [currentGalleryId])

  // 차트 데이터 변환
  const chartData = reports?.slice().reverse().map((r: DailyReport) => ({
    date: format(new Date(r.report_date), 'MM/dd', { locale: ko }),
    posts: r.total_posts,
    views: r.total_views,
  })) || []

  if (reportLoading) {
    return (
      <div className="loading-state h-96" data-state="loading">
        <div className="loading-text">데이터를 불러오는 중...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8" data-page="dashboard">
      {/* Header */}
      <header className="page-header" data-section="header">
        <h1 className="page-title">대시보드</h1>
        <p className="page-description">
          {latestReport
            ? `최근 업데이트: ${format(new Date(latestReport.report_date), 'yyyy년 MM월 dd일', { locale: ko })}`
            : '데이터가 없습니다. 크롤링을 시작하세요.'
          }
        </p>
        <p className="text-xs text-gray-400 mt-1">
          뤼튼 마이너갤 | AI챗팅 마이너갤 | 아카라이브 캐릭터AI
        </p>
      </header>

      {/* Stats Grid */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-4" data-section="stats">
        <StatCard
          title="게시글"
          value={latestReport?.total_posts || 0}
        />
        <StatCard
          title="조회수"
          value={latestReport?.total_views || 0}
        />
        <StatCard
          title="추천수"
          value={latestReport?.total_recommends || 0}
        />
        <StatCard
          title="댓글"
          value={latestReport?.total_comments || 0}
        />
      </section>

      {/* 인기 게시글 with Tabs */}
      <section className="card p-6" data-section="popular-posts">
        <div className="mb-4">
          <h3 className="section-title mb-3">인기 게시글</h3>

          {/* Tabs */}
          <div className="tab-list" data-component="gallery-tabs">
            {GALLERY_TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-item ${activeTab === tab.id ? 'tab-item--active' : ''}`}
                data-tab={tab.id}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <p className="section-subtitle mt-3">
            최근 7일 추천수 기준 TOP 15 (공지사항 제외)
          </p>
        </div>

        {postsLoading ? (
          <div className="empty-state" data-state="loading">
            데이터를 불러오는 중...
          </div>
        ) : !popularPosts || popularPosts.length === 0 ? (
          <div className="empty-state" data-state="empty">
            인기 게시글이 없습니다. 크롤링을 시작하세요.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table" data-component="posts-table">
              <thead>
                <tr className="table-header-row">
                  <th className="table-header-cell text-left w-12">순위</th>
                  <th className="table-header-cell text-left">제목</th>
                  {activeTab === 'all' && (
                    <th className="table-header-cell text-left w-32">갤러리</th>
                  )}
                  <th className="table-header-cell text-right w-20">추천</th>
                  <th className="table-header-cell text-right w-20">조회</th>
                  <th className="table-header-cell text-right w-20">댓글</th>
                </tr>
              </thead>
              <tbody>
                {popularPosts.map((post: Post, idx: number) => (
                  <tr
                    key={post.id}
                    className="table-row"
                    data-post-id={post.id}
                  >
                    <td className="table-cell text-gray-700 font-medium">{idx + 1}</td>
                    <td className="table-cell">
                      {post.url ? (
                        <a
                          href={post.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-900 hover:text-gray-600 transition-colors line-clamp-1"
                          title={post.title}
                        >
                          {post.title}
                        </a>
                      ) : (
                        <span className="text-gray-900 line-clamp-1" title={post.title}>
                          {post.title}
                        </span>
                      )}
                    </td>
                    {activeTab === 'all' && (
                      <td className="table-cell text-gray-600 text-xs">{post.gallery_id}</td>
                    )}
                    <td className="table-cell text-right text-gray-900 font-medium">
                      {post.recommend_count.toLocaleString()}
                    </td>
                    <td className="table-cell text-right text-gray-600">
                      {post.view_count.toLocaleString()}
                    </td>
                    <td className="table-cell text-right text-gray-600">
                      {post.comment_count.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Charts */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6" data-section="charts">
        {/* 게시글 트렌드 */}
        <div className="card p-6" data-chart="posts-trend">
          <h3 className="section-title mb-4">게시글 트렌드</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12, fill: '#757575' }}
                axisLine={{ stroke: '#E0E0E0' }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#757575' }}
                axisLine={{ stroke: '#E0E0E0' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E0E0E0',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}
              />
              <Area
                type="monotone"
                dataKey="posts"
                stroke="#424242"
                fill="#9E9E9E"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* 조회수 트렌드 */}
        <div className="card p-6" data-chart="views-trend">
          <h3 className="section-title mb-4">조회수 트렌드</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12, fill: '#757575' }}
                axisLine={{ stroke: '#E0E0E0' }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#757575' }}
                axisLine={{ stroke: '#E0E0E0' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E0E0E0',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}
              />
              <Area
                type="monotone"
                dataKey="views"
                stroke="#424242"
                fill="#757575"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* 키워드 분석 */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6" data-section="keywords">
        <div className="lg:col-span-2">
          <h3 className="section-title mb-3">인기 키워드</h3>
          <KeywordCloud
            keywords={latestReport?.top_keywords?.map((k: any) => ({
              text: k.keyword,
              value: k.count
            })) || []}
          />
        </div>
        <div>
          <h3 className="section-title mb-3">키워드 순위</h3>
          <RankingList
            title="TOP 10"
            items={latestReport?.top_keywords?.slice(0, 10).map((k: any, idx: number) => ({
              rank: idx + 1,
              name: k.keyword,
              score: k.count
            })) || []}
          />
        </div>
      </section>
    </div>
  )
}
