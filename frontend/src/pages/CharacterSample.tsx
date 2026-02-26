import { useCallback, useState, useMemo, useEffect } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchChatServiceCharacters, ChatServiceCharacter, generateCharacterSamples, PasswordRequiredError } from '../utils/api'
import { RefreshCw, AlertCircle, Download, Save, ChevronDown, ChevronRight, Trash2, X, FolderOpen, Lock } from 'lucide-react'

// 금지 조합 (서로 어울리지 않는 태그 쌍)
const FORBIDDEN_PAIRS: [string, string][] = [
  ['순애', 'NTR'],
  ['순애', '네토라레'],
  ['마법소녀', '무협'],
  ['마법소녀', '강호'],
  ['서양', '무협'],
  ['서양', '강호'],
  ['금발', '무협'],
  ['현대', '중세'],
  ['SF', '무협'],
  ['로봇', '판타지'],
  ['좀비', '순애'],
  ['공포', '힐링'],
  ['학원', '회사'],
  ['고등학생', '직장인'],
  ['어린이', '성인'],
]

interface TagCooccurrence {
  tag1: string
  tag2: string
  count: number
}

interface GeneratedSample {
  id: number
  title: string              // 작품 제목
  description: string        // 작품 소개글
  name: string               // 캐릭터명
  profile: string            // 캐릭터 프로필 (외모+성격+말투)
  backgroundIntro: string    // 배경 소개글
  worldPrompt: string        // 세계관 프롬프트
  firstDaySituation: string  // 첫날 상황
  openingMessage: string     // 시작 메시지
  genre: string              // 대표 장르
  hashtags: string[]         // 해시태그
  tags: string[]             // 기존 태그 (호환용)
  basedOn: string[]          // 참고한 인기 캐릭터
}

interface SavedSample extends GeneratedSample {
  savedAt: string  // ISO date string
  savedId: string  // unique id for saved samples
}

// 태그 공동 출현 분석
function analyzeTagCooccurrence(characters: ChatServiceCharacter[]): TagCooccurrence[] {
  const pairCounts = new Map<string, number>()

  characters.forEach(char => {
    const tags = char.tags || []
    for (let i = 0; i < tags.length; i++) {
      for (let j = i + 1; j < tags.length; j++) {
        const pair = [tags[i], tags[j]].sort().join('|||')
        pairCounts.set(pair, (pairCounts.get(pair) || 0) + 1)
      }
    }
  })

  return Array.from(pairCounts.entries())
    .map(([pair, count]) => {
      const [tag1, tag2] = pair.split('|||')
      return { tag1, tag2, count }
    })
    .filter(p => p.count >= 2) // 2회 이상 같이 나온 것만
    .sort((a, b) => b.count - a.count)
}

// 금지 조합 체크
function isForbiddenCombination(tags: string[]): boolean {
  const lowerTags = tags.map(t => t.toLowerCase())

  for (const [forbidden1, forbidden2] of FORBIDDEN_PAIRS) {
    const f1 = forbidden1.toLowerCase()
    const f2 = forbidden2.toLowerCase()

    if (lowerTags.some(t => t.includes(f1)) && lowerTags.some(t => t.includes(f2))) {
      return true
    }
  }
  return false
}

// 생성 횟수 제한 관리
const DAILY_LIMIT = 50
const STORAGE_KEY = 'character_sample_usage'
const SAVED_SAMPLES_KEY = 'character_saved_samples'

interface UsageData {
  count: number
  date: string
}

function getUsageData(): UsageData {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (!stored) {
    return { count: 0, date: new Date().toDateString() }
  }

  const data: UsageData = JSON.parse(stored)
  const today = new Date().toDateString()

  // 날짜가 바뀌면 카운터 리셋
  if (data.date !== today) {
    return { count: 0, date: today }
  }

  return data
}

function incrementUsage(): number {
  const data = getUsageData()
  const newCount = data.count + 1
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    count: newCount,
    date: data.date
  }))
  return newCount
}

// 저장된 샘플 관리
function getSavedSamples(): SavedSample[] {
  const stored = localStorage.getItem(SAVED_SAMPLES_KEY)
  if (!stored) return []
  try {
    return JSON.parse(stored)
  } catch {
    return []
  }
}

function saveSample(sample: GeneratedSample): SavedSample {
  const savedSamples = getSavedSamples()
  const savedSample: SavedSample = {
    ...sample,
    savedAt: new Date().toISOString(),
    savedId: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }
  savedSamples.unshift(savedSample) // 최신순으로 앞에 추가
  localStorage.setItem(SAVED_SAMPLES_KEY, JSON.stringify(savedSamples))
  return savedSample
}

function removeSavedSample(savedId: string): void {
  const savedSamples = getSavedSamples()
  const filtered = savedSamples.filter(s => s.savedId !== savedId)
  localStorage.setItem(SAVED_SAMPLES_KEY, JSON.stringify(filtered))
}

// 아코디언 아이템 컴포넌트
function AccordionItem({
  sample,
  isExpanded,
  onToggle,
  onDelete,
  onDownload
}: {
  sample: SavedSample
  isExpanded: boolean
  onToggle: () => void
  onDelete: () => void
  onDownload: () => void
}) {
  const savedDate = new Date(sample.savedAt).toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      {/* 아코디언 헤더 */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-500 flex-shrink-0" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500 flex-shrink-0" />
          )}
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {sample.name}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {sample.genre} · {savedDate}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1 flex-shrink-0" onClick={e => e.stopPropagation()}>
          <button
            onClick={onDownload}
            className="p-1.5 text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            title="CSV 다운로드"
          >
            <Download className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onDelete}
            className="p-1.5 text-gray-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
            title="삭제"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </button>

      {/* 아코디언 내용 */}
      {isExpanded && (
        <div className="p-4 space-y-3 bg-white dark:bg-gray-900 text-sm">
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              작품 제목
            </label>
            <p className="text-gray-800 dark:text-gray-200">{sample.title}</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              작품 소개
            </label>
            <p className="text-gray-600 dark:text-gray-400">{sample.description}</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              캐릭터 프로필
            </label>
            <p className="text-gray-600 dark:text-gray-400">{sample.profile}</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              시작 메시지
            </label>
            <p className="text-gray-600 dark:text-gray-400 italic">"{sample.openingMessage}"</p>
          </div>
          <div className="flex flex-wrap gap-1 pt-2">
            {sample.hashtags.map((tag, idx) => (
              <span
                key={idx}
                className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function CharacterSample() {
  const [samples, setSamples] = useState<GeneratedSample[]>([])
  const [savedSamples, setSavedSamples] = useState<SavedSample[]>([])
  const [generating, setGenerating] = useState(false)
  const [usageCount, setUsageCount] = useState<number>(0)
  const [error, setError] = useState<string>('')
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // 비밀번호 관련 state
  const [showPasswordInput, setShowPasswordInput] = useState(false)
  const [password, setPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [pendingTagPairs, setPendingTagPairs] = useState<string[][] | null>(null)

  const { data: characters, loading } = useApi(
    useCallback(() => fetchChatServiceCharacters(undefined, 180), [])
  )

  // CSV 다운로드 함수
  const downloadCSV = (sample: GeneratedSample | SavedSample) => {
    const csvRows = [
      ['필드', '내용'],
      ['작품 제목', sample.title],
      ['작품 소개글', sample.description],
      ['캐릭터 이름', sample.name],
      ['캐릭터 프로필', sample.profile],
      ['배경 소개글', sample.backgroundIntro],
      ['세계관 프롬프트', sample.worldPrompt],
      ['첫날 상황', sample.firstDaySituation],
      ['시작 메시지', sample.openingMessage],
      ['대표 장르', sample.genre],
      ['해시태그', sample.hashtags.join(', ')],
      ['참고 캐릭터', sample.basedOn.join(', ')]
    ]

    const csvContent = csvRows
      .map(row => row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(','))
      .join('\n')

    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `캐릭터샘플_${sample.name}_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  // 샘플 저장
  const handleSave = (sample: GeneratedSample) => {
    saveSample(sample)
    setSavedSamples(getSavedSamples())
    // 저장 후 현재 생성된 샘플에서 제거 (선택적)
    setSamples(prev => prev.filter(s => s.id !== sample.id))
  }

  // 저장된 샘플 삭제
  const handleDelete = (savedId: string) => {
    removeSavedSample(savedId)
    setSavedSamples(getSavedSamples())
    setExpandedIds(prev => {
      const next = new Set(prev)
      next.delete(savedId)
      return next
    })
  }

  // 아코디언 토글
  const toggleExpand = (savedId: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      if (next.has(savedId)) {
        next.delete(savedId)
      } else {
        next.add(savedId)
      }
      return next
    })
  }

  // 컴포넌트 마운트 시 사용 횟수 및 저장된 샘플 로드
  useEffect(() => {
    const data = getUsageData()
    setUsageCount(data.count)
    setSavedSamples(getSavedSamples())
  }, [])

  // 태그 공동 출현 분석
  const cooccurrence = useMemo(() => {
    if (!characters) return []
    return analyzeTagCooccurrence(characters)
  }, [characters])

  // 샘플 생성 (Gemini API 사용)
  const handleGenerate = async (inputPassword?: string) => {
    if (!characters) return
    if (usageCount >= DAILY_LIMIT) return

    setGenerating(true)
    setError('')
    setPasswordError('')

    try {
      // 태그 조합 선택 (공동 출현 빈도 기반)
      const validPairs = cooccurrence.filter(p => !isForbiddenCombination([p.tag1, p.tag2]))
      if (validPairs.length === 0) {
        throw new Error('유효한 태그 조합을 찾을 수 없습니다.')
      }

      // 상위 20개 중에서 랜덤 1개 선택
      const topPairs = validPairs.slice(0, Math.min(20, validPairs.length))
      const selectedPairs: string[][] = pendingTagPairs || []

      if (selectedPairs.length === 0) {
        const pair = topPairs[Math.floor(Math.random() * topPairs.length)]
        selectedPairs.push([pair.tag1, pair.tag2])
      }

      // Gemini API 호출 (비밀번호 포함)
      const apiSamples = await generateCharacterSamples(selectedPairs, inputPassword)

      // 성공 시 비밀번호 모달 닫기 및 pendingTagPairs 초기화
      setShowPasswordInput(false)
      setPassword('')
      setPendingTagPairs(null)

      // GeneratedSample 형식으로 변환
      const newSamples: GeneratedSample[] = apiSamples.map((sample) => ({
        id: sample.id,
        title: sample.title,
        description: sample.description,
        name: sample.name,
        profile: sample.profile,
        backgroundIntro: sample.backgroundIntro,
        worldPrompt: sample.worldPrompt,
        firstDaySituation: sample.firstDaySituation,
        openingMessage: sample.openingMessage,
        genre: sample.genre,
        hashtags: sample.hashtags || [],
        tags: sample.tags || [],
        basedOn: sample.basedOn || []
      }))

      setSamples(newSamples)

      // 사용 횟수 증가
      const newCount = incrementUsage()
      setUsageCount(newCount)

    } catch (err: any) {
      console.error('샘플 생성 오류:', err)

      // 비밀번호가 필요한 경우
      if (err instanceof PasswordRequiredError) {
        // 태그 조합 저장
        const validPairs = cooccurrence.filter(p => !isForbiddenCombination([p.tag1, p.tag2]))
        const topPairs = validPairs.slice(0, Math.min(20, validPairs.length))
        const pair = topPairs[Math.floor(Math.random() * topPairs.length)]
        setPendingTagPairs([[pair.tag1, pair.tag2]])
        setShowPasswordInput(true)
        setGenerating(false)
        return
      }

      // 비밀번호 틀림 (입력된 비밀번호가 있는 경우)
      if (inputPassword && err.message?.includes('비밀번호')) {
        setPasswordError('비밀번호가 올바르지 않습니다.')
        // pendingTagPairs는 이미 저장되어 있음 (처음 시도 시 저장됨)
        setShowPasswordInput(true)
        setGenerating(false)
        return
      }

      setError(err.message || '캐릭터 샘플 생성에 실패했습니다.')
    } finally {
      setGenerating(false)
    }
  }

  // 비밀번호 입력 후 재시도
  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!password.trim()) {
      setPasswordError('비밀번호를 입력해주세요.')
      return
    }

    // 모달을 즉시 닫고 메인 버튼에서 로딩 표시
    const enteredPassword = password
    setShowPasswordInput(false)
    setPassword('')
    setPasswordError('')

    // 메인 버튼에서 로딩하면서 생성 시도
    handleGenerate(enteredPassword)
  }

  // 비밀번호 모달 닫기
  const handleCancelPassword = () => {
    setShowPasswordInput(false)
    setPassword('')
    setPasswordError('')
    setPendingTagPairs(null)
  }

  // 남은 횟수 계산
  const remainingCount = Math.max(0, DAILY_LIMIT - usageCount)
  const isLimitReached = usageCount >= DAILY_LIMIT

  // 인기 태그 조합 TOP 10
  const topCombinations = useMemo(() => {
    return cooccurrence.slice(0, 10)
  }, [cooccurrence])

  if (loading) {
    return (
      <div className="loading-state h-96" data-state="loading">
        <div className="loading-text">데이터를 불러오는 중...</div>
      </div>
    )
  }

  return (
    <div className="flex relative" data-page="character-sample">
      {/* 메인 콘텐츠 영역 */}
      <div className="flex-1 space-y-6 min-w-0">
        {/* 헤더 */}
        <header className="page-header" data-section="header">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="page-title">캐릭터 샘플</h1>
              <p className="page-description">인기 순위 기반 캐릭터 제작 가이드</p>
            </div>
            {/* 모바일: 저장된 샘플 토글 버튼 */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <FolderOpen className="w-4 h-4" />
              <span>저장됨</span>
              {savedSamples.length > 0 && (
                <span className="bg-blue-600 text-white text-xs px-1.5 py-0.5 rounded-full">
                  {savedSamples.length}
                </span>
              )}
            </button>
          </div>
        </header>

        {/* 설명 카드 */}
        <section className="card p-6" data-section="info">
          <h3 className="section-title mb-3">이 기능은?</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mb-3">
            <strong>Google Gemini AI</strong>를 활용하여 인기 캐릭터 패턴 기반의
            고품질 캐릭터 제작 가이드를 자동 생성합니다.
            실제 인기 캐릭터들의 <strong>설명, 세계관, 태그</strong>를 분석하여
            외모, 성격, 배경까지 구체적으로 제안합니다.
          </p>
          <div className="text-xs text-gray-500 dark:text-gray-500 bg-blue-50 dark:bg-blue-900/20 rounded p-2 border border-blue-200 dark:border-blue-800">
            🤖 <strong className="text-blue-700 dark:text-blue-300">Gemini 2.5 Flash</strong> 모델 사용 ·
            하루 최대 <strong className="text-blue-700 dark:text-blue-300">{DAILY_LIMIT}회</strong> 생성 가능 ·
            매일 자정 초기화
          </div>
        </section>

        {/* 인기 태그 조합 */}
        <section className="card p-6" data-section="popular-combinations">
          <h3 className="section-title mb-4">인기 태그 조합 TOP 10</h3>
          <div className="flex flex-wrap gap-2">
            {topCombinations.map((combo, idx) => (
              <div
                key={idx}
                className="inline-flex items-center gap-1 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-full text-sm"
              >
                <span className="text-gray-500 dark:text-gray-400 text-xs mr-1">
                  {idx + 1}.
                </span>
                <span className="font-medium text-gray-800 dark:text-gray-200">
                  #{combo.tag1}
                </span>
                <span className="text-gray-400">+</span>
                <span className="font-medium text-gray-800 dark:text-gray-200">
                  #{combo.tag2}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">
                  ({combo.count}회)
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* 생성 버튼 / 비밀번호 입력 */}
        <div className="flex flex-col items-center gap-3">
          {showPasswordInput ? (
            /* 비밀번호 입력 폼 */
            <div className="flex flex-col items-center gap-3">
              <form onSubmit={handlePasswordSubmit} className="flex items-center gap-2">
                {/* 비밀번호 입력 컨테이너 */}
                <div className="flex items-center gap-2 px-6 py-3 bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 rounded">
                  <Lock className="w-4 h-4 text-gray-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value)
                      setPasswordError('')
                    }}
                    placeholder="비밀번호를 입력하세요"
                    className="flex-1 bg-transparent text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none text-sm"
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={handleCancelPassword}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                    title="취소"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                {/* 확인 버튼 */}
                <button
                  type="submit"
                  className="px-6 py-3 bg-white dark:bg-white text-black border border-gray-200 dark:border-gray-800 rounded hover:bg-gray-50 transition-colors font-medium"
                >
                  확인
                </button>
              </form>
              {passwordError && (
                <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {passwordError}
                </p>
              )}
            </div>
          ) : (
            /* 생성 버튼 */
            <button
              onClick={() => handleGenerate()}
              disabled={generating || !characters || isLimitReached}
              className="crawl-button flex items-center gap-2 px-6 py-3"
              data-action="generate"
            >
              <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
              {generating ? 'Gemini AI 생성 중...' : isLimitReached ? '오늘의 생성 횟수 초과' : '캐릭터 샘플 생성'}
            </button>
          )}

          {/* 에러 메시지 */}
          {error && (
            <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 px-4 py-2 rounded">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}

          {/* 남은 횟수 표시 */}
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {isLimitReached ? (
              <span className="text-red-500 dark:text-red-400 font-medium">
                오늘의 생성 횟수를 모두 사용했습니다. 내일 다시 시도해주세요.
              </span>
            ) : (
              <>
                오늘 남은 생성 횟수: <span className="font-semibold text-gray-900 dark:text-white">{remainingCount}</span>회 / {DAILY_LIMIT}회
              </>
            )}
          </div>
        </div>

        {/* 생성된 샘플 */}
        {samples.length > 0 && (
          <section className="space-y-4" data-section="samples">
            <h3 className="section-title">생성된 캐릭터 가이드</h3>

            <div className="grid grid-cols-1 gap-6">
              {samples.map(sample => (
                <div
                  key={sample.id}
                  className="card p-6 space-y-5"
                  data-sample-id={sample.id}
                >
                  {/* 헤더: 작품 제목 + 장르 + 태그 */}
                  <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs font-medium rounded">
                        {sample.genre}
                      </span>
                    </div>
                    <h4 className="font-bold text-gray-900 dark:text-white text-lg mb-2">
                      {sample.title}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {sample.description}
                    </p>
                    <div className="flex items-center justify-between gap-3 flex-wrap">
                      <div className="flex flex-wrap gap-1">
                        {sample.hashtags.map((tag, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleSave(sample)}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600 rounded transition-colors whitespace-nowrap"
                          title="저장하기"
                        >
                          <Save className="w-3.5 h-3.5" />
                          저장
                        </button>
                        <button
                          onClick={() => downloadCSV(sample)}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-[#0a0a0a] border border-gray-300 dark:border-gray-700 rounded hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors whitespace-nowrap"
                          title="CSV로 추출"
                        >
                          <Download className="w-3.5 h-3.5" />
                          CSV
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* 캐릭터 정보 */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                        캐릭터 이름
                      </label>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 p-3 rounded">
                        {sample.name}
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                        캐릭터 프로필
                      </label>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 p-3 rounded">
                        {sample.profile}
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                        배경 소개글
                      </label>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 p-3 rounded">
                        {sample.backgroundIntro}
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                        세계관 프롬프트
                      </label>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 p-3 rounded">
                        {sample.worldPrompt}
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                        첫날 상황
                      </label>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 p-3 rounded">
                        {sample.firstDaySituation}
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                        시작 메시지
                      </label>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 p-3 rounded">
                        "{sample.openingMessage}"
                      </p>
                    </div>
                  </div>

                  {/* 참고 캐릭터 */}
                  {sample.basedOn && sample.basedOn.length > 0 && (
                    <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                      <span className="text-xs text-gray-500 dark:text-gray-500">
                        참고 캐릭터: {sample.basedOn.join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* 안내 */}
        <section className="card p-6 bg-gray-50 dark:bg-gray-800/50" data-section="notice">
          <h3 className="section-title mb-3">사용 안내</h3>
          <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1 list-disc list-inside">
            <li><strong>Gemini AI</strong>가 실제 인기 캐릭터를 분석하여 창의적인 가이드를 생성합니다.</li>
            <li>태그 조합은 공동 출현 빈도가 높은 조합 중에서 자동 선택됩니다.</li>
            <li>어울리지 않는 조합(예: 서양+무협, 순애+NTR)은 자동으로 제외됩니다.</li>
            <li>매번 다른 결과가 생성되며, <strong>외모, 성격, 세계관, 스토리</strong>까지 제공됩니다.</li>
            <li>완전 무료로 사용 가능하며, 하루 {DAILY_LIMIT}회 제한이 있습니다.</li>
            <li><strong>저장</strong> 버튼을 클릭하면 샘플이 브라우저에 저장되어 페이지 이동 후에도 유지됩니다.</li>
          </ul>
        </section>
      </div>

      {/* 데스크탑: 오른쪽 사이드바 */}
      <aside className="hidden lg:block w-80 ml-6 flex-shrink-0">
        <div className="sticky top-6">
          <div className="card p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <FolderOpen className="w-4 h-4" />
                저장된 샘플
              </h3>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {savedSamples.length}개
              </span>
            </div>

            {savedSamples.length === 0 ? (
              <div className="text-center py-8 text-sm text-gray-500 dark:text-gray-400">
                <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p>저장된 샘플이 없습니다.</p>
                <p className="text-xs mt-1">캐릭터 생성 후 저장해보세요!</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[calc(100vh-200px)] overflow-y-auto">
                {savedSamples.map(sample => (
                  <AccordionItem
                    key={sample.savedId}
                    sample={sample}
                    isExpanded={expandedIds.has(sample.savedId)}
                    onToggle={() => toggleExpand(sample.savedId)}
                    onDelete={() => handleDelete(sample.savedId)}
                    onDownload={() => downloadCSV(sample)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* 모바일: 바텀시트 오버레이 */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          {/* 배경 오버레이 */}
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setSidebarOpen(false)}
          />

          {/* 바텀시트 */}
          <div className="absolute bottom-0 left-0 right-0 bg-white dark:bg-gray-900 rounded-t-2xl shadow-xl max-h-[80vh] flex flex-col animate-slide-up">
            {/* 핸들 바 */}
            <div className="flex justify-center py-3">
              <div className="w-12 h-1.5 bg-gray-300 dark:bg-gray-600 rounded-full" />
            </div>

            {/* 헤더 */}
            <div className="flex items-center justify-between px-4 pb-3 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <FolderOpen className="w-4 h-4" />
                저장된 샘플
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ({savedSamples.length}개)
                </span>
              </h3>
              <button
                onClick={() => setSidebarOpen(false)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 콘텐츠 */}
            <div className="flex-1 overflow-y-auto p-4">
              {savedSamples.length === 0 ? (
                <div className="text-center py-8 text-sm text-gray-500 dark:text-gray-400">
                  <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-30" />
                  <p>저장된 샘플이 없습니다.</p>
                  <p className="text-xs mt-1">캐릭터 생성 후 저장해보세요!</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {savedSamples.map(sample => (
                    <AccordionItem
                      key={sample.savedId}
                      sample={sample}
                      isExpanded={expandedIds.has(sample.savedId)}
                      onToggle={() => toggleExpand(sample.savedId)}
                      onDelete={() => handleDelete(sample.savedId)}
                      onDownload={() => downloadCSV(sample)}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 바텀시트 애니메이션 스타일 */}
      <style>{`
        @keyframes slide-up {
          from {
            transform: translateY(100%);
          }
          to {
            transform: translateY(0);
          }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>

    </div>
  )
}
