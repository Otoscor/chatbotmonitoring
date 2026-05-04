/**
 * 캐릭터 샘플 관련 타입 정의
 */
import { CHARACTER_SAMPLE, FORBIDDEN_TAG_PAIRS } from '../../config'

export interface TagCooccurrence {
  tag1: string
  tag2: string
  count: number
}

export interface GeneratedSample {
  id: number
  title: string              // 작품 제목
  description: string        // 작품 소개글
  name: string               // 캐릭터명
  profile: string            // 캐릭터 프로필 (외모+성격+말투)
  appearancePrompt: string   // 미드저니용 외모 묘사 프롬프트 (영어)
  backgroundIntro: string    // 배경 소개글
  worldPrompt: string        // 세계관 프롬프트
  firstDaySituation: string  // 첫날 상황
  openingMessage: string     // 시작 메시지
  genre: string              // 대표 장르
  hashtags: string[]         // 해시태그
  tags: string[]             // 기존 태그 (호환용)
  basedOn: string[]          // 참고한 인기 캐릭터
}

export interface SavedSample extends GeneratedSample {
  savedAt: string  // ISO date string
  savedId: string  // unique id for saved samples
}

export interface UsageData {
  count: number
  date: string
}

// 상수 (config에서 재내보내기)
export const FORBIDDEN_PAIRS = FORBIDDEN_TAG_PAIRS
export const DAILY_LIMIT = CHARACTER_SAMPLE.DAILY_LIMIT
export const STORAGE_KEY = CHARACTER_SAMPLE.STORAGE_KEY
export const SAVED_SAMPLES_KEY = CHARACTER_SAMPLE.SAVED_SAMPLES_KEY
