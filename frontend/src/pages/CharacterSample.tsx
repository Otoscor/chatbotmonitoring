import { useCallback, useState, useMemo, useEffect } from 'react'
import { useApi } from '../hooks/useApi'
import { fetchChatServiceCharacters, ChatServiceCharacter, generateCharacterSamples, CharacterSample as ApiCharacterSample } from '../utils/api'
import { RefreshCw, AlertCircle, Download } from 'lucide-react'

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

// 외모 키워드 (태그에서 추출 가능한 것들)
const APPEARANCE_KEYWORDS = ['금발', '흑발', '은발', '적발', '백발', '갈색머리', '장발', '단발', '포니테일', '트윈테일']

// 성격 키워드
const PERSONALITY_KEYWORDS = ['츤데레', '얀데레', '쿨데레', '단데레', '천연', '활발', '조용한', '냉정', '다정', '장난꾸러기']

// 장르 키워드
const GENRE_KEYWORDS = ['판타지', '현대', 'SF', '무협', '로맨스', '액션', '공포', '미스터리', '코미디', '힐링', '학원', '회사', '이세계']

// 설정 키워드
const SETTING_KEYWORDS = ['아카데미', '학교', '고등학교', '대학', '회사', '던전', '왕국', '제국', '도시', '마을', '숲', '우주']

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

// 태그에서 외모 추출
function extractAppearance(tags: string[]): string {
  const found = tags.filter(t =>
    APPEARANCE_KEYWORDS.some(k => t.includes(k))
  )
  if (found.length > 0) {
    return found.join(', ') + ' 스타일'
  }

  // 기본 외모 생성
  const defaults = ['단정한 외모', '개성 있는 스타일', '깔끔한 인상', '눈에 띄는 외모']
  return defaults[Math.floor(Math.random() * defaults.length)]
}

// 태그에서 성격 추출
function extractPersonality(tags: string[]): string {
  const found = tags.filter(t =>
    PERSONALITY_KEYWORDS.some(k => t.includes(k))
  )
  if (found.length > 0) {
    return found.join(', ')
  }

  // 기본 성격 생성
  const defaults = ['호기심이 많고 적극적인', '조용하지만 속마음이 따뜻한', '겉으로는 냉정하나 다정한', '밝고 활발한']
  return defaults[Math.floor(Math.random() * defaults.length)]
}

// 태그에서 설정 추출
function extractSetting(tags: string[]): string {
  const genreFound = tags.filter(t =>
    GENRE_KEYWORDS.some(k => t.includes(k))
  )
  const settingFound = tags.filter(t =>
    SETTING_KEYWORDS.some(k => t.includes(k))
  )

  const parts: string[] = []
  if (genreFound.length > 0) parts.push(genreFound[0])
  if (settingFound.length > 0) parts.push(settingFound[0])

  if (parts.length > 0) {
    return parts.join(' ') + ' 세계관'
  }

  return '현대 배경'
}

// 샘플 캐릭터 생성
function generateSamples(
  characters: ChatServiceCharacter[],
  cooccurrence: TagCooccurrence[],
  count: number
): GeneratedSample[] {
  const samples: GeneratedSample[] = []
  const usedTagSets = new Set<string>()

  // 상위 캐릭터들의 태그 조합 분석
  const topCharacters = characters.slice(0, 30)

  let attempts = 0
  const maxAttempts = 100

  while (samples.length < count && attempts < maxAttempts) {
    attempts++

    // 공동 출현 빈도가 높은 태그 쌍 선택
    const validPairs = cooccurrence.filter(p => !isForbiddenCombination([p.tag1, p.tag2]))
    if (validPairs.length === 0) break

    // 상위 태그 쌍에서 랜덤 선택 (가중치 적용)
    const topPairs = validPairs.slice(0, Math.min(20, validPairs.length))
    const selectedPair = topPairs[Math.floor(Math.random() * topPairs.length)]

    // 추가 태그 선택 (해당 태그들과 자주 나오는 것)
    const relatedTags = cooccurrence
      .filter(p =>
        (p.tag1 === selectedPair.tag1 || p.tag1 === selectedPair.tag2 ||
         p.tag2 === selectedPair.tag1 || p.tag2 === selectedPair.tag2) &&
        p.tag1 !== selectedPair.tag1 && p.tag1 !== selectedPair.tag2 &&
        p.tag2 !== selectedPair.tag1 && p.tag2 !== selectedPair.tag2
      )
      .slice(0, 10)

    // 최종 태그 조합
    let finalTags = [selectedPair.tag1, selectedPair.tag2]

    if (relatedTags.length > 0) {
      const extraTag = relatedTags[Math.floor(Math.random() * relatedTags.length)]
      const newTag = extraTag.tag1 === selectedPair.tag1 || extraTag.tag1 === selectedPair.tag2
        ? extraTag.tag2
        : extraTag.tag1
      finalTags.push(newTag)
    }

    // 금지 조합 체크
    if (isForbiddenCombination(finalTags)) continue

    // 중복 체크
    const tagSetKey = [...finalTags].sort().join(',')
    if (usedTagSets.has(tagSetKey)) continue
    usedTagSets.add(tagSetKey)

    // 참고한 캐릭터 찾기
    const basedOnChars = topCharacters
      .filter(c => {
        const charTags = c.tags || []
        return finalTags.some(t => charTags.includes(t))
      })
      .slice(0, 2)
      .map(c => c.name)

    // 샘플 생성
    const sample: GeneratedSample = {
      id: samples.length + 1,
      name: `${finalTags[0]} ${finalTags[1] || ''} 캐릭터`.trim(),
      tags: finalTags,
      appearance: extractAppearance(finalTags),
      personality: extractPersonality(finalTags),
      setting: extractSetting(finalTags),
      description: generateDescription(finalTags),
      basedOn: basedOnChars
    }

    samples.push(sample)
  }

  return samples
}

// 설명 생성
function generateDescription(tags: string[]): string {
  const templates = [
    `{{user}}는 ${tags[0]} 세계에서 모험을 시작합니다. ${tags[1] || '새로운'} 요소가 가득한 이곳에서 당신만의 이야기를 만들어보세요.`,
    `${tags[0]}과(와) ${tags[1] || '흥미로운 요소'}가 결합된 세계관입니다. 당신은 이곳에서 어떤 존재로 살아갈 것인가요?`,
    `이곳은 ${tags[0]}의 세계입니다. ${tags[1] || '다양한'} 캐릭터들과 함께 당신의 상상력을 펼쳐보세요.`,
  ]

  return templates[Math.floor(Math.random() * templates.length)]
}

// 생성 횟수 제한 관리
const DAILY_LIMIT = 50
const STORAGE_KEY = 'character_sample_usage'

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

export default function CharacterSample() {
  const [samples, setSamples] = useState<GeneratedSample[]>([])
  const [generating, setGenerating] = useState(false)
  const [usageCount, setUsageCount] = useState<number>(0)
  const [error, setError] = useState<string>('')

  const { data: characters, loading } = useApi(
    useCallback(() => fetchChatServiceCharacters(undefined, 180), [])
  )

  // CSV 다운로드 함수
  const downloadCSV = (sample: GeneratedSample) => {
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

  // 컴포넌트 마운트 시 사용 횟수 로드
  useEffect(() => {
    const data = getUsageData()
    setUsageCount(data.count)
  }, [])

  // 태그 공동 출현 분석
  const cooccurrence = useMemo(() => {
    if (!characters) return []
    return analyzeTagCooccurrence(characters)
  }, [characters])

  // 샘플 생성 (Gemini API 사용)
  const handleGenerate = async () => {
    if (!characters) return
    if (usageCount >= DAILY_LIMIT) return

    setGenerating(true)
    setError('')

    try {
      // 태그 조합 선택 (공동 출현 빈도 기반)
      const validPairs = cooccurrence.filter(p => !isForbiddenCombination([p.tag1, p.tag2]))
      if (validPairs.length === 0) {
        throw new Error('유효한 태그 조합을 찾을 수 없습니다.')
      }

      // 상위 20개 중에서 랜덤 1개 선택
      const topPairs = validPairs.slice(0, Math.min(20, validPairs.length))
      const selectedPairs: string[][] = []

      const pair = topPairs[Math.floor(Math.random() * topPairs.length)]
      selectedPairs.push([pair.tag1, pair.tag2])

      // Gemini API 호출
      const apiSamples = await generateCharacterSamples(selectedPairs)

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
      setError(err.message || '캐릭터 샘플 생성에 실패했습니다.')
    } finally {
      setGenerating(false)
    }
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
    <div className="space-y-6" data-page="character-sample">
      {/* 헤더 */}
      <header className="page-header" data-section="header">
        <h1 className="page-title">캐릭터 샘플</h1>
        <p className="page-description">인기 순위 기반 캐릭터 제작 가이드</p>
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

      {/* 생성 버튼 */}
      <div className="flex flex-col items-center gap-3">
        <button
          onClick={handleGenerate}
          disabled={generating || !characters || isLimitReached}
          className="crawl-button flex items-center gap-2 px-6 py-3"
          data-action="generate"
        >
          <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
          {generating ? 'Gemini AI 생성 중...' : isLimitReached ? '오늘의 생성 횟수 초과' : '캐릭터 샘플 생성'}
        </button>

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
                  <div className="flex items-center justify-between gap-3">
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
                    <button
                      onClick={() => downloadCSV(sample)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-[#0a0a0a] border border-gray-300 dark:border-gray-700 rounded hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors whitespace-nowrap"
                      title="CSV로 추출"
                    >
                      <Download className="w-3.5 h-3.5" />
                      CSV 추출
                    </button>
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
        </ul>
      </section>
    </div>
  )
}
