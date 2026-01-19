import { useCallback } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchChatServiceCharacters, fetchPopularTags, ChatServiceCharacter, PopularTag } from '../utils/api'
import KeywordCloud from '../components/KeywordCloud'

export default function CharacterRankings() {
  const { data: characters, loading } = useApi(
    useCallback(() => fetchChatServiceCharacters(undefined, 150), [])
  )

  const { data: popularTags, loading: tagsLoading } = useApi(
    useCallback(() => fetchPopularTags(20), [])
  )

  // 서비스별로 그룹화
  const groupedCharacters = {
    zeta: characters?.filter((c: ChatServiceCharacter) => c.service === 'zeta') || [],
    lunatalk: characters?.filter((c: ChatServiceCharacter) => c.service === 'lunatalk') || [],
    babechat: characters?.filter((c: ChatServiceCharacter) => c.service === 'babechat') || [],
    crack: characters?.filter((c: ChatServiceCharacter) => c.service === 'crack') || []
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
        <h1 className="text-2xl font-semibold text-gray-900 mb-1">캐릭터 순위</h1>
        <p className="text-sm text-gray-500">인기 캐릭터챗 서비스의 TOP 캐릭터</p>
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

      {/* 4열 레이아웃 - 반응형 (데스크톱 4열, 태블릿 2열, 모바일 1열) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* 제타 섹션 */}
        {groupedCharacters.zeta.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Zeta</h2>
              <span className="text-sm text-gray-500">{groupedCharacters.zeta.length}개</span>
            </div>
            <div className="text-xs text-gray-500 -mt-2 mb-2">전체 인기순</div>
            
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
            <div className="text-xs text-gray-500 -mt-2 mb-2">일간 랭킹</div>
            
            <div className="space-y-3">
              {groupedCharacters.lunatalk.map((char: ChatServiceCharacter) => (
                <CharacterCard key={char.id} character={char} formatViews={formatViews} />
              ))}
            </div>
          </div>
        )}

        {/* 베이비챗 섹션 */}
        {groupedCharacters.babechat.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">BabeChat</h2>
              <span className="text-sm text-gray-500">{groupedCharacters.babechat.length}개</span>
            </div>
            <div className="text-xs text-gray-500 -mt-2 mb-2">인기순</div>
            
            <div className="space-y-3">
              {groupedCharacters.babechat.map((char: ChatServiceCharacter) => (
                <CharacterCard key={char.id} character={char} formatViews={formatViews} />
              ))}
            </div>
          </div>
        )}

        {/* 크랙 섹션 */}
        {groupedCharacters.crack.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Crack</h2>
              <span className="text-sm text-gray-500">{groupedCharacters.crack.length}개</span>
            </div>
            <div className="text-xs text-gray-500 -mt-2 mb-2">대화 횟수순</div>
            
            <div className="space-y-3">
              {groupedCharacters.crack.map((char: ChatServiceCharacter) => (
                <CharacterCard key={char.id} character={char} formatViews={formatViews} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 데이터 없음 */}
      {groupedCharacters.zeta.length === 0 && groupedCharacters.babechat.length === 0 && groupedCharacters.lunatalk.length === 0 && groupedCharacters.crack.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">크롤링된 캐릭터 데이터가 없습니다.</p>
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
  // BabeChat과 Crack은 모달 형식이므로 직접 링크 없음
  const hasDirectLink = !['babechat', 'crack'].includes(character.service)
  
  const cardContent = (
    <div className="flex gap-3">
      {/* 순위 */}
      <div className="flex-shrink-0">
        <span className="inline-flex items-center justify-center w-7 h-7 text-sm font-medium text-gray-700 bg-gray-100 rounded">
          {character.rank}
        </span>
      </div>

      {/* 컨텐츠 */}
      <div className="flex-1 min-w-0 space-y-2">
        {/* 이름 - 최대 2줄 */}
        <h3 className="text-sm font-medium text-gray-900 line-clamp-2 leading-snug" title={character.name}>
          {character.name}
        </h3>

        {/* 조회수 */}
        {character.views > 0 && (
          <p className="text-xs text-gray-500">{formatViews(character.views)} 조회</p>
        )}

        {/* 해시태그 - 최대 3개 */}
        {character.tags && Array.isArray(character.tags) && character.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {character.tags.slice(0, 3).map((tag, idx) => (
              <span 
                key={idx}
                className="inline-block px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
              >
                #{tag}
              </span>
            ))}
            {character.tags.length > 3 && (
              <span className="inline-block px-1.5 py-0.5 text-xs text-gray-400">
                +{character.tags.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
  
  // 직접 링크가 있는 경우 (Zeta, LunaTalk) - <a> 태그 사용
  if (hasDirectLink) {
    return (
      <a
        href={character.character_url || '#'}
        target="_blank"
        rel="noopener noreferrer"
        className="block bg-white border border-gray-200 rounded p-4 hover:border-gray-300 hover:shadow-sm transition-all overflow-hidden"
      >
        {cardContent}
      </a>
    )
  }
  
  // 직접 링크가 없는 경우 (BabeChat, Crack) - <div> 태그로 동일한 스타일 적용
  return (
    <div className="block bg-white border border-gray-200 rounded p-4 hover:border-gray-300 hover:shadow-sm transition-all overflow-hidden">
      {cardContent}
    </div>
  )
}
