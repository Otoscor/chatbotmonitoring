import { useState, useCallback } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchChatServiceCharacters, triggerChatServiceCrawl, fetchPopularTags, USE_STATIC_DATA, ChatServiceCharacter, PopularTag } from '../utils/api'
import KeywordCloud from '../components/KeywordCloud'

export default function CharacterRankings() {
  const [crawling, setCrawling] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  
  const { data: characters, loading, refetch } = useApi(
    useCallback(() => fetchChatServiceCharacters(), [])
  )

  const { data: popularTags, loading: tagsLoading } = useApi(
    useCallback(() => fetchPopularTags(20), [])
  )

  const handleCrawl = async () => {
    setCrawling(true)
    setMessage(null)
    
    try {
      const result = await triggerChatServiceCrawl(['zeta', 'babechat', 'lunatalk'])
      if (result.success) {
        setMessage({ type: 'success', text: result.message })
        await refetch()
      } else {
        setMessage({ type: 'error', text: result.message })
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: `크롤링 실패: ${error.message}` })
    } finally {
      setCrawling(false)
    }
  }

  // 서비스별로 그룹화
  const groupedCharacters = {
    zeta: characters?.filter((c: ChatServiceCharacter) => c.service === 'zeta') || [],
    babechat: characters?.filter((c: ChatServiceCharacter) => c.service === 'babechat') || [],
    lunatalk: characters?.filter((c: ChatServiceCharacter) => c.service === 'lunatalk') || [],
  }

  const formatViews = (views: number) => {
    if (views >= 10000) {
      return `${(views / 10000).toFixed(1)}만`
    }
    if (views >= 1000) {
      return `${(views / 1000).toFixed(1)}천`
    }
    return views.toString()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-sm text-gray-400">데이터를 불러오는 중...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="pb-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-1">캐릭터 순위</h1>
            <p className="text-sm text-gray-500">인기 캐릭터챗 서비스의 TOP 캐릭터</p>
          </div>
          {!USE_STATIC_DATA && (
            <button
              onClick={handleCrawl}
              disabled={crawling}
              className="px-4 py-2 text-sm font-medium bg-gray-900 text-white rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {crawling ? '크롤링 중...' : '데이터 갱신'}
            </button>
          )}
        </div>
        
        {message && (
          <div className={`mt-4 p-3 rounded text-sm ${
            message.type === 'success' 
              ? 'bg-gray-100 text-gray-700' 
              : 'bg-gray-900 text-white'
          }`}>
            {message.text}
          </div>
        )}
      </div>

      {/* 인기 해시태그 */}
      <div className="bg-white border border-gray-200 rounded p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">인기 해시태그</h3>
        {tagsLoading ? (
          <div className="text-center py-8 text-sm text-gray-400">
            데이터를 불러오는 중...
          </div>
        ) : !popularTags || popularTags.length === 0 ? (
          <div className="text-center py-8 text-sm text-gray-500">
            태그 데이터가 없습니다.
          </div>
        ) : (
          <KeywordCloud
            keywords={popularTags.map((tag: PopularTag) => ({
              text: `#${tag.tag}`,
              value: tag.count
            }))}
          />
        )}
      </div>

      {/* 제타 & 루나톡 2열 레이아웃 */}
      <div className="grid grid-cols-2 gap-6">
        {/* 제타 섹션 */}
        {groupedCharacters.zeta.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Zeta</h2>
              <span className="text-sm text-gray-500">{groupedCharacters.zeta.length}개</span>
            </div>
            
            <div className="space-y-3">
              {groupedCharacters.zeta.map((char: ChatServiceCharacter) => (
                <CharacterCard key={char.id} character={char} formatViews={formatViews} />
              ))}
            </div>
          </div>
        )}

        {/* 루나톡 섹션 */}
        {groupedCharacters.lunatalk.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">LUNATALK</h2>
              <span className="text-sm text-gray-500">{groupedCharacters.lunatalk.length}개</span>
            </div>
            
            <div className="space-y-3">
              {groupedCharacters.lunatalk.map((char: ChatServiceCharacter) => (
                <CharacterCard key={char.id} character={char} formatViews={formatViews} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 베이비챗 섹션 (전체 너비) */}
      {groupedCharacters.babechat.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">BabeChat</h2>
            <span className="text-sm text-gray-500">{groupedCharacters.babechat.length}개</span>
          </div>
          
          <div className="space-y-3">
            {groupedCharacters.babechat.map((char: ChatServiceCharacter) => (
              <CharacterCard key={char.id} character={char} formatViews={formatViews} />
            ))}
          </div>
        </div>
      )}

      {/* 데이터 없음 */}
      {groupedCharacters.zeta.length === 0 && groupedCharacters.babechat.length === 0 && groupedCharacters.lunatalk.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">크롤링된 캐릭터 데이터가 없습니다.</p>
          <button
            onClick={handleCrawl}
            className="px-4 py-2 text-sm font-medium bg-gray-900 text-white rounded hover:bg-gray-800 transition-colors"
          >
            크롤링 시작
          </button>
        </div>
      )}
    </div>
  )
}

// 캐릭터 카드 컴포넌트
function CharacterCard({ 
  character, 
  formatViews 
}: { 
  character: ChatServiceCharacter
  formatViews: (views: number) => string
}) {
  return (
    <a
      href={character.character_url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-white border border-gray-200 rounded p-4 hover:border-gray-300 transition-all h-36 overflow-hidden"
    >
      <div className="flex gap-4 h-full">
        {/* 순위 */}
        <div className="flex-shrink-0">
          <span className="inline-flex items-center justify-center w-8 h-8 text-sm font-medium text-gray-700 bg-gray-100 rounded">
            {character.rank}
          </span>
        </div>

        {/* 컨텐츠 */}
        <div className="flex-1 min-w-0 flex flex-col">
          {/* 이름 - 최대 1줄 */}
          <h3 className="text-base font-medium text-gray-900 mb-1 line-clamp-1" title={character.name}>
            {character.name}
          </h3>

          {/* 조회수 */}
          {character.views > 0 && (
            <p className="text-sm text-gray-500 mb-2 flex-shrink-0">{formatViews(character.views)} 조회</p>
          )}

          {/* 설명 - 최대 2줄 */}
          {character.description && (
            <p className="text-sm text-gray-600 mb-2 line-clamp-2" title={character.description}>
              {character.description}
            </p>
          )}

          {/* 해시태그 - 최대 4개, 1줄 */}
          {character.tags && Array.isArray(character.tags) && character.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-auto overflow-hidden" style={{ maxHeight: '2rem' }}>
              {character.tags.slice(0, 4).map((tag, idx) => (
                <span 
                  key={idx}
                  className="inline-block px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded whitespace-nowrap"
                >
                  #{tag}
                </span>
              ))}
              {character.tags.length > 4 && (
                <span className="inline-block px-2 py-0.5 text-xs text-gray-400">
                  +{character.tags.length - 4}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </a>
  )
}
