import { useCallback } from 'react'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import { useApi } from '../hooks/useApi'
import { fetchReports, type DailyReport } from '../utils/api'

export default function Reports() {
  const { data: reports, loading } = useApi(
    useCallback(() => fetchReports(0, 30), [])
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-sm text-gray-400">데이터를 불러오는 중...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="pb-6 border-b border-gray-200">
        <h1 className="text-2xl font-semibold text-gray-900 mb-1">리포트</h1>
        <p className="text-sm text-gray-500">일별 크롤링 리포트 내역</p>
      </div>

      <div className="bg-white border border-gray-200 rounded">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-900">날짜</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-900">게시글</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-900">조회수</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-900">추천수</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-900">댓글</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {!reports || reports.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-gray-400">
                    리포트 데이터가 없습니다
                  </td>
                </tr>
              ) : (
                reports.map((report: DailyReport) => (
                  <tr key={report.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-gray-900">
                      {format(new Date(report.report_date), 'yyyy년 MM월 dd일', { locale: ko })}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {report.total_posts.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {report.total_views.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {report.total_recommends.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {report.total_comments.toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
