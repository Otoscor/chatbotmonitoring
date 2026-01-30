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
      <div className="loading-state h-96" data-state="loading">
        <div className="loading-text">데이터를 불러오는 중...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6" data-page="reports">
      <header className="page-header" data-section="header">
        <h1 className="page-title">리포트</h1>
        <p className="page-description">일별 크롤링 리포트 내역</p>
      </header>

      <section className="card" data-section="reports-table">
        <div className="overflow-x-auto">
          <table className="data-table" data-component="reports-table">
            <thead>
              <tr className="table-header-row">
                <th className="table-header-cell--left">날짜</th>
                <th className="table-header-cell--right">게시글</th>
                <th className="table-header-cell--right">조회수</th>
                <th className="table-header-cell--right">추천수</th>
                <th className="table-header-cell--right">댓글</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {!reports || reports.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-gray-400" data-state="empty">
                    리포트 데이터가 없습니다
                  </td>
                </tr>
              ) : (
                reports.map((report: DailyReport) => {
                  return (
                    <tr
                      key={report.id}
                      className="table-row"
                      data-report-id={report.id}
                    >
                      <td className="table-cell--left">
                        {format(new Date(report.report_date), 'yyyy년 MM월 dd일', { locale: ko })}
                      </td>
                      <td className="table-cell--right">
                        {report.total_posts.toLocaleString()}
                      </td>
                      <td className="table-cell--right">
                        {report.total_views.toLocaleString()}
                      </td>
                      <td className="table-cell--right">
                        {report.total_recommends.toLocaleString()}
                      </td>
                      <td className="table-cell--right">
                        {report.total_comments.toLocaleString()}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

