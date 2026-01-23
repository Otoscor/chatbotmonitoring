import { useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import { useApi } from '../hooks/useApi'
import {
  fetchReportByDate,
  fetchReportKeywords,
  fetchReportCharacters,
  fetchReportTags,
  type ReportCharacter,
  type PopularTag
} from '../utils/api'
import StatCard from '../components/StatCard'
import KeywordCloud from '../components/KeywordCloud'

export default function ReportDetail() {
  const { date } = useParams<{ date: string }>()

  const { data: report, loading: reportLoading } = useApi(
    useCallback(() => date ? fetchReportByDate(date) : Promise.reject(), [date])
  )

  const { data: keywords, loading: keywordsLoading } = useApi(
    useCallback(() => date ? fetchReportKeywords(date, 30) : Promise.resolve([]), [date])
  )

  const { data: characters, loading: charactersLoading } = useApi(
    useCallback(() => date ? fetchReportCharacters(date, 20) : Promise.resolve([]), [date])
  )

  const { data: tags, loading: tagsLoading } = useApi(
    useCallback(() => date ? fetchReportTags(date, 20) : Promise.resolve([]), [date])
  )

  if (reportLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-sm text-gray-400">데이터를 불러오는 중...</div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <div className="text-sm text-gray-500 mb-4">해당 날짜의 리포트가 없습니다.</div>
        <Link
          to="/reports"
          className="px-4 py-2 text-sm bg-gray-900 text-white rounded hover:bg-gray-800 transition-colors"
        >
          리포트 목록으로
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header with Back Button */}
      <div className="flex items-center gap-4 pb-6 border-b border-gray-200">
        <Link
          to="/reports"
          className="text-gray-500 hover:text-gray-900 transition-colors"
        >
          ← 리포트 목록
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-semibold text-gray-900 mb-1">
            {date && format(new Date(date), 'yyyy년 MM월 dd일', { locale: ko })} 리포트
          </h1>
          <p className="text-sm text-gray-500">
            뤼튼 마이너갤 | AI챗팅 마이너갤 | 아카라이브 캐릭터AI
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="게시글"
          value={report.total_posts || 0}
        />
        <StatCard
          title="조회수"
          value={report.total_views || 0}
        />
        <StatCard
          title="추천수"
          value={report.total_recommends || 0}
        />
        <StatCard
          title="댓글"
          value={report.total_comments || 0}
        />
      </div>

      {/* Keywords Section */}
      <div className="bg-white border border-gray-200 rounded p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">인기 키워드</h3>
        {keywordsLoading ? (
          <div className="text-center py-8 text-sm text-gray-400">
            데이터를 불러오는 중...
          </div>
        ) : !keywords || keywords.length === 0 ? (
          <div className="text-center py-8 text-sm text-gray-500">
            키워드 데이터가 없습니다.
          </div>
        ) : (
          <KeywordCloud keywords={keywords} />
        )}
      </div>

      {/* Tags Section */}
      <div className="bg-white border border-gray-200 rounded p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">인기 해시태그</h3>
        {tagsLoading ? (
          <div className="text-center py-8 text-sm text-gray-400">
            데이터를 불러오는 중...
          </div>
        ) : !tags || tags.length === 0 ? (
          <div className="text-center py-8 text-sm text-gray-500">
            태그 데이터가 없습니다.
          </div>
        ) : (
          <KeywordCloud
            keywords={tags.map((tag: PopularTag) => ({
              text: `#${tag.tag}`,
              value: tag.count
            }))}
          />
        )}
      </div>

      {/* Characters Section */}
      <div className="bg-white border border-gray-200 rounded p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">인기 캐릭터</h3>
        {charactersLoading ? (
          <div className="text-center py-8 text-sm text-gray-400">
            데이터를 불러오는 중...
          </div>
        ) : !characters || characters.length === 0 ? (
          <div className="text-center py-8 text-sm text-gray-500">
            캐릭터 데이터가 없습니다.
          </div>
        ) : (
          <div className="space-y-2">
            {characters.map((character: ReportCharacter, index: number) => (
              <div
                key={character.name}
                className="flex items-center justify-between py-2 px-3 hover:bg-gray-50 rounded transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-400 w-6">
                    {index + 1}
                  </span>
                  <span className="text-sm text-gray-900">{character.name}</span>
                </div>
                <span className="text-sm text-gray-500">
                  {character.mentions.toLocaleString()}회 언급
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
