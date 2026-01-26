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
      <div className="flex items-center justify-center h-96">
        <div className="text-sm text-gray-400">데이터를 불러오는 중...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="pb-6 border-b border-gray-200">
        <h1 className="text-2xl font-semibold text-gray-900 mb-1">대시보드</h1>
        <p className="text-sm text-gray-500">
          {latestReport
            ? `최근 업데이트: ${format(new Date(latestReport.report_date), 'yyyy년 MM월 dd일', { locale: ko })}`
            : '데이터가 없습니다. 크롤링을 시작하세요.'
          }
        </p>
        <p className="text-xs text-gray-400 mt-1">
          뤼튼 마이너갤 | AI챗팅 마이너갤 | 아카라이브 캐릭터AI
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
      </div>

      {/* 인기 게시글 with Tabs */}
      <div className="bg-white border border-gray-200 rounded p-6">
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">인기 게시글</h3>

          {/* Tabs */}
          <div className="flex space-x-1 border-b border-gray-200">
            {GALLERY_TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  px-4 py-2 text-sm font-medium transition-colors
                  ${activeTab === tab.id
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-500 hover:text-gray-700'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <p className="text-xs text-gray-500 mt-3">
            최근 7일 추천수 기준 TOP 15 (공지사항 제외)
          </p>
        </div>

        {postsLoading ? (
          <div className="text-center py-8 text-sm text-gray-400">
            데이터를 불러오는 중...
          </div>
        ) : !popularPosts || popularPosts.length === 0 ? (
          <div className="text-center py-8 text-sm text-gray-500">
            인기 게시글이 없습니다. 크롤링을 시작하세요.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 font-medium text-gray-700 w-12">순위</th>
                  <th className="text-left py-2 px-3 font-medium text-gray-700">제목</th>
                  {activeTab === 'all' && (
                    <th className="text-left py-2 px-3 font-medium text-gray-700 w-32">갤러리</th>
                  )}
                  <th className="text-right py-2 px-3 font-medium text-gray-700 w-20">추천</th>
                  <th className="text-right py-2 px-3 font-medium text-gray-700 w-20">조회</th>
                  <th className="text-right py-2 px-3 font-medium text-gray-700 w-20">댓글</th>
                </tr>
              </thead>
              <tbody>
                {popularPosts.map((post: Post, idx: number) => (
                  <tr
                    key={post.id}
                    className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                  >
                    <td className="py-2 px-3 text-gray-700 font-medium">{idx + 1}</td>
                    <td className="py-2 px-3">
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
                      <td className="py-2 px-3 text-gray-600 text-xs">{post.gallery_id}</td>
                    )}
                    <td className="py-2 px-3 text-right text-gray-900 font-medium">
                      {post.recommend_count.toLocaleString()}
                    </td>
                    <td className="py-2 px-3 text-right text-gray-600">
                      {post.view_count.toLocaleString()}
                    </td>
                    <td className="py-2 px-3 text-right text-gray-600">
                      {post.comment_count.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 게시글 트렌드 */}
        <div className="bg-white border border-gray-200 rounded p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">게시글 트렌드</h3>
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
        <div className="bg-white border border-gray-200 rounded p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">조회수 트렌드</h3>
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
      </div>

      {/* 키워드 분석 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">인기 키워드</h3>
          <KeywordCloud
            keywords={latestReport?.top_keywords?.map((k: any) => ({
              text: k.keyword,
              value: k.count
            })) || []}
          />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-gray-900 mb-3">키워드 순위</h3>
          <RankingList
            title="TOP 10"
            items={latestReport?.top_keywords?.slice(0, 10).map((k: any, idx: number) => ({
              rank: idx + 1,
              name: k.keyword,
              score: k.count
            })) || []}
          />
        </div>
      </div>
    </div>
  )
}
