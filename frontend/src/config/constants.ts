/**
 * 앱 전역 상수
 *
 * 하드코딩된 값들을 중앙 관리합니다.
 */

// 캐릭터 샘플 생성 설정
export const CHARACTER_SAMPLE = {
  DAILY_LIMIT: 50,
  STORAGE_KEY: 'character_sample_usage',
  SAVED_SAMPLES_KEY: 'character_saved_samples',
} as const

// 캐릭터 랭킹 설정
export const CHARACTER_RANKING = {
  ITEMS_PER_PAGE: 4,
  DEFAULT_DAYS: 7,
} as const

// API 설정
export const API = {
  DEFAULT_LIMIT: 50,
  DEFAULT_SKIP: 0,
  MAX_LIMIT: 200,
} as const

// UI 설정
export const UI = {
  MOBILE_BREAKPOINT: 768,
  ANIMATION_DURATION: 300,
} as const

// 금지 태그 조합 (서로 어울리지 않는 태그 쌍)
export const FORBIDDEN_TAG_PAIRS: readonly [string, string][] = [
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
] as const
