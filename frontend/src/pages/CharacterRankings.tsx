import { useCallback, useState } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchChatServiceCharacters, fetchPopularTags, ChatServiceCharacter, PopularTag } from '../utils/api'
import NetworkGraph from '../components/NetworkGraph'
import { ChevronLeft, ChevronRight } from 'lucide-react'

// 서비스 설정
const SERVICE_CONFIG = [
  { id: 'zeta', label: 'Zeta', subtext: '전체 인기순', directLink: true },
  { id: 'lunatalk', label: 'LUNATALK', subtext: '일간 랭킹', directLink: true },
  { id: 'babechat', label: 'BabeChat', subtext: '인기순', directLink: false },
  { id: 'crack', label: 'Crack', subtext: '대화 횟수순', directLink: false },
  { id: 'elyn', label: 'Elyn', subtext: '랭킹', directLink: true },
  { id: 'caveduck', label: 'Caveduck', subtext: '랭킹', directLink: true }
]

const ITEMS_PER_PAGE = 4

export default function CharacterRankings() {
  const [currentPage, setCurrentPage] = useState(0)
  const [activeService, setActiveService] = useState('zeta') // For mobile tabs

  const { data: characters, loading } = useApi(
    useCallback(() => fetchChatServiceCharacters(undefined, 180), []) // 30 per service * 6 = 180
  )

  const { data: popularTags, loading: tagsLoading } = useApi(
    useCallback(() => fetchPopularTags(20), [])
  )

  const formatViews = (views: number) => {
    if (views >= 10000) {
      return `${(views / 10000).toFixed(1)}만`
    }
    if (views >= 1000) {
      return `${(views / 1000).toFixed(1)}천`
    }
    return views.toString()
  }

  // 페이지 이동 핸들러
  const totalPages = Math.ceil(SERVICE_CONFIG.length / ITEMS_PER_PAGE)
  const nextPage = () => setCurrentPage(prev => Math.min(prev + 1, totalPages - 1))
  const prevPage = () => setCurrentPage(prev => Math.max(prev - 1, 0))

  // 현재 페이지에 보여줄 서비스들
  const currentServices = SERVICE_CONFIG.slice(
    currentPage * ITEMS_PER_PAGE,
    (currentPage + 1) * ITEMS_PER_PAGE
  )

  if (loading) {
    return (
      <div className="loading-state h-96" data-state="loading">
        <div className="loading-text">데이터를 불러오는 중...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6" data-page="character-rankings">
      {/* 헤더 */}
      <header className="page-header" data-section="header">
        <h1 className="page-title">캐릭터 순위</h1>
        <p className="page-description">인기 캐릭터챗 서비스의 TOP 캐릭터</p>
      </header>

      {/* 인기 해시태그 */}
      <section className="card p-6 relative" data-section="popular-hashtags">
        <h3 className="section-title mb-4">인기 해시태그</h3>
        {tagsLoading ? (
          <div className="empty-state" data-state="loading">
            데이터를 불러오는 중...
          </div>
        ) : !popularTags || popularTags.length === 0 ? (
          <div className="empty-state" data-state="empty">
            태그 데이터가 없습니다.
          </div>
        ) : (
          <>
            <NetworkGraph
              keywords={popularTags.map((tag: PopularTag) => ({
                text: `#${tag.tag}`,
                value: tag.count
              }))}
            />
            <div className="absolute bottom-4 right-4 flex flex-row items-end gap-3 pointer-events-none select-none opacity-60 z-10">
              <span className="text-[12px] text-gray-500 dark:text-gray-400 font-medium">마우스 휠 확대/축소</span>
              <span className="text-[12px] text-gray-500 dark:text-gray-400 font-medium">마우스 패닝 이동</span>
            </div>
          </>
        )}
      </section>

      {/* 캐릭터 순위 영역 */}
      <section className="relative" data-section="character-rankings">
        {/* 모바일 서비스 탭 */}
        <div className="md:hidden mb-6 sticky top-[56px] z-30 bg-[var(--bg-primary)] py-2 border-b border-[var(--border-primary)]">
          <div className="tab-list overflow-x-auto whitespace-nowrap flex-nowrap scrollbar-hide" data-component="service-tabs">
            {SERVICE_CONFIG.map(service => (
              <button
                key={service.id}
                onClick={() => setActiveService(service.id)}
                className={`tab-item ${activeService === service.id ? 'tab-item--active' : ''} inline-block px-4 py-2`}
                data-tab={service.id}
              >
                {service.label}
              </button>
            ))}
          </div>
        </div>

        {/* 데스크톱 네비게이션 버튼 (좌) */}
        <div className="hidden md:block">
          {currentPage > 0 && (
            <button
              onClick={prevPage}
              className="carousel-nav-button carousel-nav-prev group"
              aria-label="이전 페이지"
              data-action="prev"
            >
              <ChevronLeft className="carousel-nav-icon group-hover:text-gray-900" />
            </button>
          )}
        </div>

        {/* 데스크톱 네비게이션 버튼 (우) */}
        <div className="hidden md:block">
          {currentPage < totalPages - 1 && (
            <button
              onClick={nextPage}
              className="carousel-nav-button carousel-nav-next group"
              aria-label="다음 페이지"
              data-action="next"
            >
              <ChevronRight className="carousel-nav-icon group-hover:text-gray-900" />
            </button>
          )}
        </div>

        {/* 모바일: 선택된 서비스만 표시 */}
        <div className="md:hidden space-y-6">
          {SERVICE_CONFIG.filter(s => s.id === activeService).map((serviceConfig) => {
            const serviceCharacters = characters?.filter(
              (c: ChatServiceCharacter) => c.service === serviceConfig.id
            ) || []

            return (
              <div key={serviceConfig.id} className="space-y-4" data-service={serviceConfig.id}>
                <div className="flex items-center justify-between">
                  <h2 className="service-title">{serviceConfig.label}</h2>
                  <span className="text-count">{serviceCharacters.length}개</span>
                </div>
                <div className="section-subtitle -mt-2 mb-2">{serviceConfig.subtext}</div>

                <div className="space-y-3">
                  {serviceCharacters.length > 0 ? (
                    serviceCharacters.map((char: ChatServiceCharacter) => (
                      <CharacterCard
                        key={char.id}
                        character={char}
                        formatViews={formatViews}
                        directLink={serviceConfig.directLink}
                      />
                    ))
                  ) : (
                    <div className="empty-state--dashed" data-state="empty">
                      <p>데이터가 없습니다</p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* 데스크톱: 4열 그리드 캐러셀 */}
        <div className="hidden md:block">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" data-component="service-grid">
            {currentServices.map((serviceConfig) => {
              const serviceCharacters = characters?.filter(
                (c: ChatServiceCharacter) => c.service === serviceConfig.id
              ) || []

              return (
                <div key={serviceConfig.id} className="space-y-4" data-service={serviceConfig.id}>
                  <div className="flex items-center justify-between">
                    <h2 className="service-title">{serviceConfig.label}</h2>
                    <span className="text-count">{serviceCharacters.length}개</span>
                  </div>
                  <div className="section-subtitle -mt-2 mb-2">{serviceConfig.subtext}</div>

                  <div className="space-y-3">
                    {serviceCharacters.length > 0 ? (
                      serviceCharacters.map((char: ChatServiceCharacter) => (
                        <CharacterCard
                          key={char.id}
                          character={char}
                          formatViews={formatViews}
                          directLink={serviceConfig.directLink}
                        />
                      ))
                    ) : (
                      <div className="empty-state--dashed" data-state="empty">
                        <p>데이터가 없습니다</p>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* 전체 데이터 없음 */}
      {(!characters || characters.length === 0) && (
        <div className="empty-state py-12" data-state="no-data">
          <p className="text-gray-500">크롤링된 캐릭터 데이터가 없습니다.</p>
        </div>
      )}
    </div>
  )
}

// 캐릭터 카드 컴포넌트
function CharacterCard({
  character,
  formatViews,
  directLink
}: {
  character: ChatServiceCharacter
  formatViews: (views: number) => string
  directLink: boolean
}) {
  const cardContent = (
    <div className="character-card-content h-full">
      {/* 순위 */}
      <div className="flex-shrink-0">
        <span className="character-rank-badge">
          {character.rank}
        </span>
      </div>

      {/* 컨텐츠 */}
      <div className="character-info flex flex-col h-full">
        <div className="flex-1 min-h-0">
          {/* 이름 - 최대 2줄 */}
          <h3 className="character-name text-sm font-medium leading-snug line-clamp-2 mb-1" title={character.name}>
            {character.name}
          </h3>

          {/* 조회수 */}
          {character.views > 0 && (
            <p className="character-views text-xs text-gray-500 dark:text-gray-400 mb-2">{formatViews(character.views)} 조회</p>
          )}
        </div>

        {/* 해시태그 - 가로 스크롤 */}
        <div className="h-6 flex items-end overflow-hidden">
          {character.tags && Array.isArray(character.tags) && character.tags.length > 0 && (
            <div className="character-tags flex flex-nowrap gap-1 overflow-x-auto scrollbar-hide w-full mask-linear-fade">
              {character.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="character-tag text-[10px] px-1.5 py-0.5 whitespace-nowrap bg-gray-100 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-300 flex-shrink-0"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )

  // 직접 링크가 있는 경우 (Zeta, LunaTalk, Elyn, Caveduck) - <a> 태그 사용
  if (directLink) {
    return (
      <a
        href={character.character_url || '#'}
        target="_blank"
        rel="noopener noreferrer"
        className="character-card h-[134px] flex flex-col"
        data-component="character-card"
        data-character-id={character.id}
      >
        {cardContent}
      </a>
    )
  }

  // 직접 링크가 없는 경우 (BabeChat, Crack) - <div> 태그로 동일한 스타일 적용
  return (
    <div
      className="character-card h-[134px] flex flex-col"
      data-component="character-card"
      data-character-id={character.id}
    >
      {cardContent}
    </div>
  )
}
