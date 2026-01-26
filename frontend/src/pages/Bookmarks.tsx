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
    // 개발 환경 확인 (개발 환경에서만 URL 추가 가능)
    const isDevelopment = import.meta.env.DEV

    const [bookmarks, setBookmarks] = useState<Bookmark[]>([])
    const [loading, setLoading] = useState(false)
    const [urlInput, setUrlInput] = useState('')
    const [addingBookmark, setAddingBookmark] = useState(false)

    // 북마크 목록 로드
    useEffect(() => {
        loadBookmarks()
    }, [])

    const loadBookmarks = async () => {
        setLoading(true)
        try {
            const data = await fetchBookmarks(0, 50)
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
            const newBookmark = await addBookmark(urlInput)
            setBookmarks([newBookmark, ...bookmarks])
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
        <div className="space-y-6">
            {/* Header */}
            <div className="pb-6 border-b border-gray-200">
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">북마크</h1>
                <p className="text-sm text-gray-500">
                    링크를 저장하고 AI가 자동으로 요약해드립니다
                </p>
            </div>

            {/* URL 입력 폼 (개발 환경에서만 표시) */}
            {isDevelopment && (
                <form onSubmit={handleAddBookmark} className="bg-white border border-gray-200 rounded p-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        URL 추가
                    </label>
                    <div className="flex gap-2">
                        <input
                            type="url"
                            value={urlInput}
                            onChange={(e) => setUrlInput(e.target.value)}
                            placeholder="https://example.com/article"
                            className="flex-1 px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                            disabled={addingBookmark}
                        />
                        <button
                            type="submit"
                            disabled={addingBookmark || !urlInput.trim()}
                            className="px-6 py-2 bg-gray-900 text-white rounded hover:bg-gray-800 disabled:bg-gray-400 transition-colors"
                        >
                            {addingBookmark ? '추가 중...' : '북마크 추가'}
                        </button>
                    </div>
                </form>
            )}

            {/* 북마크 리스트 */}
            {loading ? (
                <div className="text-center py-12 text-gray-500">
                    북마크를 불러오는 중...
                </div>
            ) : bookmarks.length === 0 ? (
                <div className="bg-white border border-gray-200 rounded p-12 text-center">
                    <p className="text-gray-500 mb-2">저장된 북마크가 없습니다</p>
                    {isDevelopment && (
                        <p className="text-sm text-gray-400">위에서 URL을 입력하여 첫 북마크를 추가해보세요</p>
                    )}
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {bookmarks.map((bookmark) => (
                        <div
                            key={bookmark.id}
                            className="bg-white border border-gray-200 rounded p-4 hover:border-gray-300 transition-colors"
                        >
                            <div className="flex gap-4">
                                {/* 썸네일 */}
                                {bookmark.thumbnail_url && (
                                    <div className="flex-shrink-0">
                                        <img
                                            src={bookmark.thumbnail_url}
                                            alt={bookmark.title || 'Thumbnail'}
                                            className="w-32 h-24 object-cover rounded"
                                            onError={(e) => {
                                                e.currentTarget.style.display = 'none'
                                            }}
                                        />
                                    </div>
                                )}

                                {/* 내용 */}
                                <div className="flex-1 min-w-0">
                                    {/* 제목 */}
                                    <a
                                        href={bookmark.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-lg font-medium text-gray-900 hover:text-gray-600 line-clamp-2 block mb-1"
                                    >
                                        {bookmark.title || bookmark.url}
                                    </a>

                                    {/* 사이트명 */}
                                    {bookmark.site_name && (
                                        <p className="text-xs text-gray-500 mb-2">{bookmark.site_name}</p>
                                    )}

                                    {/* AI 요약 또는 설명 */}
                                    {bookmark.is_summarized === 1 && bookmark.ai_summary ? (
                                        <div className="mb-2">
                                            <div className="text-xs text-blue-600 font-medium mb-1">✨ AI 요약</div>
                                            <p className="text-sm text-gray-700 line-clamp-3">{bookmark.ai_summary}</p>
                                        </div>
                                    ) : bookmark.is_summarized === 0 ? (
                                        <p className="text-sm text-gray-400 italic mb-2">요약 생성 중...</p>
                                    ) : bookmark.description ? (
                                        <p className="text-sm text-gray-600 line-clamp-2 mb-2">{bookmark.description}</p>
                                    ) : null}

                                    {/* 메타 정보 */}
                                    <div className="flex items-center gap-4 text-xs text-gray-500">
                                        <span>{format(new Date(bookmark.created_at), 'yyyy년 MM월 dd일', { locale: ko })}</span>

                                        {/* 버튼들 */}
                                        <div className="flex gap-2 ml-auto">
                                            {bookmark.is_summarized === 2 && (
                                                <button
                                                    onClick={() => handleResummary(bookmark.id)}
                                                    className="text-blue-600 hover:text-blue-800"
                                                >
                                                    요약 재생성
                                                </button>
                                            )}
                                            <button
                                                onClick={() => handleDelete(bookmark.id)}
                                                className="text-red-600 hover:text-red-800"
                                            >
                                                삭제
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
