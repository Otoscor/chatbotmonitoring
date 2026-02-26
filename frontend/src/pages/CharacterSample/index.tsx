/**
 * 캐릭터 샘플 페이지
 *
 * 인기 캐릭터 패턴 기반의 캐릭터 제작 가이드를 Gemini AI로 자동 생성합니다.
 */
import { useCallback, useState, useMemo, FormEvent } from 'react'
import { Folder } from '@nsmr/pixelart-react'
import { useApi } from '../../hooks/useApi'
import {
  fetchChatServiceCharacters,
  ChatServiceCharacter,
  generateCharacterSamples,
  PasswordRequiredError
} from '../../utils/api'

// 타입 및 상수
import {
  GeneratedSample,
  TagCooccurrence,
  FORBIDDEN_PAIRS,
  DAILY_LIMIT
} from './types'

// 커스텀 훅
import { useUsageLimit, useSavedSamples, usePasswordProtection } from './hooks'

// 컴포넌트
import {
  TagCombinations,
  PasswordForm,
  GenerateButton,
  GeneratedSampleCard,
  SavedSamplesSidebar
} from './components'

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
    .filter(p => p.count >= 2)
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

// CSV 다운로드 함수
function downloadCSV(sample: GeneratedSample) {
  const csvRows = [
    ['필드', '내용'],
    ['작품 제목', sample.title],
    ['작품 소개글', sample.description],
    ['캐릭터 이름', sample.name],
    ['캐릭터 프로필', sample.profile],
    ['외모 묘사 (Midjourney)', sample.appearancePrompt || ''],
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

export default function CharacterSample() {
  // 상태
  const [samples, setSamples] = useState<GeneratedSample[]>([])
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string>('')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // 커스텀 훅
  const { remainingCount, isLimitReached, incrementUsage, dailyLimit } = useUsageLimit()
  const { savedSamples, saveSample, removeSample, toggleExpand, isExpanded } = useSavedSamples()
  const password = usePasswordProtection()

  // 캐릭터 데이터 로드
  const { data: characters, loading } = useApi(
    useCallback(() => fetchChatServiceCharacters(undefined, 180), [])
  )

  // 태그 공동 출현 분석
  const cooccurrence = useMemo(() => {
    if (!characters) return []
    return analyzeTagCooccurrence(characters)
  }, [characters])

  // 인기 태그 조합 TOP 10
  const topCombinations = useMemo(() => {
    return cooccurrence.slice(0, 10)
  }, [cooccurrence])

  // 샘플 생성
  const handleGenerate = async (inputPassword?: string) => {
    if (!characters) return
    if (isLimitReached) return

    setGenerating(true)
    setError('')

    try {
      // 태그 조합 선택
      const validPairs = cooccurrence.filter(p => !isForbiddenCombination([p.tag1, p.tag2]))
      if (validPairs.length === 0) {
        throw new Error('유효한 태그 조합을 찾을 수 없습니다.')
      }

      // 상위 20개 중에서 랜덤 1개 선택
      const topPairs = validPairs.slice(0, Math.min(20, validPairs.length))
      const selectedPairs: string[][] = password.pendingTagPairs || []

      if (selectedPairs.length === 0) {
        const pair = topPairs[Math.floor(Math.random() * topPairs.length)]
        selectedPairs.push([pair.tag1, pair.tag2])
      }

      // Gemini API 호출
      const apiSamples = await generateCharacterSamples(selectedPairs, inputPassword)

      // 성공 시 초기화
      password.handleCancel()

      // GeneratedSample 형식으로 변환
      const newSamples: GeneratedSample[] = apiSamples.map((sample) => ({
        id: sample.id,
        title: sample.title,
        description: sample.description,
        name: sample.name,
        profile: sample.profile,
        appearancePrompt: sample.appearancePrompt || '',
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
      incrementUsage()

    } catch (err: unknown) {
      console.error('샘플 생성 오류:', err)

      // 비밀번호가 필요한 경우
      if (err instanceof PasswordRequiredError) {
        const validPairs = cooccurrence.filter(p => !isForbiddenCombination([p.tag1, p.tag2]))
        const topPairs = validPairs.slice(0, Math.min(20, validPairs.length))
        const pair = topPairs[Math.floor(Math.random() * topPairs.length)]
        password.requestPassword([[pair.tag1, pair.tag2]])
        setGenerating(false)
        return
      }

      // 비밀번호 틀림
      const errorObj = err as { response?: { status: number }; message?: string }
      const isPasswordError = inputPassword && (
        errorObj.response?.status === 401 ||
        errorObj.message === '비밀번호가 올바르지 않습니다.'
      )

      if (isPasswordError) {
        password.setError('비밀번호가 올바르지 않습니다.')
        setGenerating(false)
        return
      }

      setError(errorObj.message || '캐릭터 샘플 생성에 실패했습니다.')
    } finally {
      setGenerating(false)
    }
  }

  // 비밀번호 제출
  const handlePasswordSubmit = (e: FormEvent) => {
    e.preventDefault()
    const enteredPassword = password.submitPassword()
    if (enteredPassword) {
      handleGenerate(enteredPassword)
    }
  }

  // 저장 핸들러
  const handleSave = (sample: GeneratedSample) => {
    saveSample(sample)
    setSamples(prev => prev.filter(s => s.id !== sample.id))
  }

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
              <Folder className="w-4 h-4" />
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
        <TagCombinations combinations={topCombinations} />

        {/* 생성 버튼 / 비밀번호 입력 */}
        <div className="flex flex-col items-center gap-3">
          {password.showPasswordInput ? (
            <PasswordForm
              password={password.password}
              passwordError={password.passwordError}
              formRef={password.passwordFormRef}
              onPasswordChange={password.handlePasswordChange}
              onClear={password.clearPassword}
              onSubmit={handlePasswordSubmit}
            />
          ) : (
            <GenerateButton
              generating={generating}
              disabled={generating || !characters || isLimitReached}
              isLimitReached={isLimitReached}
              error={error}
              remainingCount={remainingCount}
              dailyLimit={dailyLimit}
              onClick={() => handleGenerate()}
            />
          )}
        </div>

        {/* 생성된 샘플 */}
        {samples.length > 0 && (
          <section className="space-y-4" data-section="samples">
            <h3 className="section-title">생성된 캐릭터 가이드</h3>
            <div className="grid grid-cols-1 gap-6">
              {samples.map(sample => (
                <GeneratedSampleCard
                  key={sample.id}
                  sample={sample}
                  onSave={handleSave}
                  onDownload={downloadCSV}
                />
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

      {/* 저장된 샘플 사이드바 */}
      <SavedSamplesSidebar
        samples={savedSamples}
        isExpanded={isExpanded}
        onToggle={toggleExpand}
        onDelete={removeSample}
        onDownload={downloadCSV}
        isMobileOpen={sidebarOpen}
        onMobileClose={() => setSidebarOpen(false)}
      />
    </div>
  )
}
