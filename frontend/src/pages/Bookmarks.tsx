import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import {
    addBookmark,
    fetchBookmarks,
    deleteBookmark,
    resummaryBookmark,
    type Bookmark
} from '../utils/api'

export default function Bookmarks() {
    // 배포 환경에서는 무조건 수정 불가 (개발 환경에서만 가능)
    const canEdit = import.meta.env.DEV

    const [bookmarks, setBookmarks] = useState<Bookmark[]>([])
    const [loading, setLoading] = useState(false)
    const [urlInput, setUrlInput] = useState('')
    const [addingBookmark, setAddingBookmark] = useState(false)

    // 탭 설정 (게시글, 뉴스, 창작물)
    const [activeTab, setActiveTab] = useState('post')
    const tabs = [
        { id: 'post', label: '게시글' },
        { id: 'news', label: '뉴스' },
        { id: 'creation', label: '창작물' }
    ]

    // 북마크 목록 로드
    useEffect(() => {
        loadBookmarks()
    }, [activeTab]) // 탭 변경 시 재로딩

    const loadBookmarks = async () => {
        setLoading(true)
        try {
            const data = await fetchBookmarks(0, 50, activeTab)
            setBookmarks(data)
        } catch (error) {
            console.error('Failed to load bookmarks:', error)
        } finally {
            setLoading(false)
        }
    }

    // 북마크 추가
    const handleAddBookmark = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!urlInput.trim()) return

        // URL 유효성 검사
        try {
            new URL(urlInput)
        } catch {
            alert('올바른 URL을 입력해주세요.')
            return
        }

        setAddingBookmark(true)
        try {
            // 현재 활성화된 탭의 카테고리로 북마크 추가
            const newBookmark = await addBookmark(urlInput, activeTab)
            // 현재 탭과 일치하는 경우에만 리스트에 추가 (보통 최신순이므로 맨 앞)
            if (newBookmark.category === activeTab) {
                setBookmarks([newBookmark, ...bookmarks])
            }
            setUrlInput('')
        } catch (error) {
            console.error('Failed to add bookmark:', error)
            alert('북마크 추가에 실패했습니다.')
        } finally {
            setAddingBookmark(false)
        }
    }

    // 북마크 삭제
    const handleDelete = async (id: number) => {
        if (!confirm('이 북마크를 삭제하시겠습니까?')) return

        try {
            await deleteBookmark(id)
            setBookmarks(bookmarks.filter(b => b.id !== id))
        } catch (error) {
            console.error('Failed to delete bookmark:', error)
            alert('삭제에 실패했습니다.')
        }
    }

    // AI 요약 재생성
    const handleResummary = async (id: number) => {
        try {
            const updated = await resummaryBookmark(id)
            setBookmarks(bookmarks.map(b => b.id === id ? updated : b))
        } catch (error) {
            console.error('Failed to regenerate summary:', error)
            alert('요약 재생성에 실패했습니다.')
        }
    }

    return (
        <div className="space-y-6" data-page="bookmarks">
            {/* Header */}
            <header className="page-header" data-section="header">
                <h1 className="page-title">북마크</h1>
                <p className="page-description">
                    링크를 저장하고 AI가 자동으로 요약해드립니다
                </p>
            </header>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-800 mb-6">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`tab-item ${activeTab === tab.id ? 'tab-item--active' : ''}`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* URL 입력 폼 (수정 권한이 있을 때만 표시) */}
            {canEdit && (
                <form
                    onSubmit={handleAddBookmark}
                    className="card p-6"
                    data-component="bookmark-form"
                >
                    <label className="form-label">
                        {tabs.find(t => t.id === activeTab)?.label} 추가
                    </label>
                    <div className="flex gap-2">
                        <input
                            type="url"
                            value={urlInput}
                            onChange={(e) => setUrlInput(e.target.value)}
                            placeholder={`https://example.com/article (${activeTab})`}
                            className="form-input flex-1"
                            disabled={addingBookmark}
                        />
                        <button
                            type="submit"
                            disabled={addingBookmark || !urlInput.trim()}
                            className="btn-primary"
                        >
                            {addingBookmark ? '추가 중...' : '북마크 추가'}
                        </button>
                    </div>
                </form>
            )}

            {/* 북마크 리스트 */}
            {loading ? (
                <div className="empty-state py-12" data-state="loading">
                    북마크를 불러오는 중...
                </div>
            ) : bookmarks.length === 0 ? (
                <div className="empty-state-card" data-state="empty">
                    <p className="text-gray-500 mb-2">저장된 {tabs.find(t => t.id === activeTab)?.label} 북마크가 없습니다</p>
                    {canEdit && (
                        <p className="text-sm text-gray-400">위에서 URL을 입력하여 첫 북마크를 추가해보세요</p>
                    )}
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4" data-component="bookmark-list">
                    {bookmarks.map((bookmark) => (
                        <article
                            key={bookmark.id}
                            className="bookmark-card"
                            data-bookmark-id={bookmark.id}
                        >
                            <div className="flex gap-4">
                                {/* 썸네일 */}
                                {bookmark.thumbnail_url && (
                                    <div className="flex-shrink-0">
                                        <img
                                            src={bookmark.thumbnail_url}
                                            alt={bookmark.title || 'Thumbnail'}
                                            className="bookmark-thumbnail"
                                            onError={(e) => {
                                                e.currentTarget.style.display = 'none'
                                            }}
                                        />
                                    </div>
                                )}

                                {/* 내용 */}
                                <div className="bookmark-content">
                                    {/* 제목 */}
                                    <a
                                        href={bookmark.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="bookmark-title"
                                    >
                                        {bookmark.title || bookmark.url}
                                    </a>

                                    {/* 사이트명 */}
                                    {bookmark.site_name && (
                                        <p className="bookmark-site-name">{bookmark.site_name}</p>
                                    )}

                                    {/* AI 요약 또는 설명 */}
                                    {bookmark.is_summarized === 1 && bookmark.ai_summary ? (
                                        <div className="mb-2" data-summary="ai">
                                            <div className="text-xs text-blue-600 font-medium mb-1">✨ AI 요약</div>
                                            <p className="bookmark-summary">{bookmark.ai_summary}</p>
                                        </div>
                                    ) : bookmark.is_summarized === 0 ? (
                                        <p className="text-sm text-gray-400 italic mb-2" data-summary="pending">요약 생성 중...</p>
                                    ) : bookmark.description ? (
                                        <p className="text-sm text-gray-600 line-clamp-2 mb-2">{bookmark.description}</p>
                                    ) : null}

                                    {/* 메타 정보 */}
                                    <div className="bookmark-meta">
                                        <span>{format(new Date(bookmark.created_at), 'yyyy년 MM월 dd일', { locale: ko })}</span>

                                        {/* 버튼들 */}
                                        <div className="bookmark-actions">
                                            {bookmark.is_summarized === 2 && canEdit && (
                                                <button
                                                    onClick={() => handleResummary(bookmark.id)}
                                                    className="text-blue-600 hover:text-blue-800"
                                                    data-action="resummary"
                                                >
                                                    요약 재생성
                                                </button>
                                            )}
                                            {canEdit && (
                                                <button
                                                    onClick={() => handleDelete(bookmark.id)}
                                                    className="text-red-600 hover:text-red-800"
                                                    data-action="delete"
                                                >
                                                    삭제
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </article>
                    ))}
                </div>
            )}
        </div>
    )
}
