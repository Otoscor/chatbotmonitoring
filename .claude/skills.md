# Monitoring Project Design System

이 문서는 프로젝트의 UI 구현 시 참고해야 할 디자인 시스템을 정의합니다.

---

## 색상 시스템 (Colors)

### Light Mode
| 용도 | CSS 변수 | 값 |
|------|----------|-----|
| 기본 배경 | `--bg-primary` | `#ffffff` |
| 보조 배경 | `--bg-secondary` | `#f9fafb` |
| 카드 배경 | `--bg-card` | `#ffffff` |
| 사이드바 배경 | `--bg-sidebar` | `#f9fafb` |
| 기본 텍스트 | `--text-primary` | `#111827` |
| 보조 텍스트 | `--text-secondary` | `#6b7280` |
| 3차 텍스트 | `--text-tertiary` | `#9ca3af` |
| 기본 보더 | `--border-primary` | `#e5e7eb` |
| 호버 보더 | `--border-hover` | `#d1d5db` |

### Dark Mode
| 용도 | CSS 변수 | 값 |
|------|----------|-----|
| 기본 배경 | `--bg-primary` | `#0a0a0a` |
| 보조 배경 | `--bg-secondary` | `#121212` |
| 카드 배경 | `--bg-card` | `#1a1a1a` |
| 사이드바 배경 | `--bg-sidebar` | `#0f0f0f` (black) |
| 기본 텍스트 | `--text-primary` | `#ffffff` |
| 보조 텍스트 | `--text-secondary` | `#a3a3a3` |
| 3차 텍스트 | `--text-tertiary` | `#737373` |
| 기본 보더 | `--border-primary` | `#262626` |
| 호버 보더 | `--border-hover` | `#404040` |

### Tailwind 클래스 매핑
```
Light: bg-white, bg-gray-50, border-gray-200
Dark:  dark:bg-[#0a0a0a], dark:bg-[#1a1a1a], dark:border-gray-800
```

---

## 타이포그래피 (Typography)

### 폰트 패밀리
- **본문**: `'Pretendard Variable', 'Pretendard', system-ui, sans-serif`
- **UI 요소 (네비게이션, CTA, 타이틀)**: `'Galmuri11', sans-serif`

### 텍스트 크기
| 용도 | 클래스 | 크기 |
|------|--------|------|
| 페이지 타이틀 | `text-2xl` | 24px |
| 섹션 타이틀 | `text-lg` | 18px |
| 카드 타이틀 | `text-sm font-semibold` | 14px |
| 본문 | `text-sm` | 14px |
| 네비게이션 | `text-[13px]` | 13px |
| 캡션/메타 | `text-xs` | 12px |

---

## 간격 (Spacing)

### 패딩
| 요소 | 값 |
|------|-----|
| 카드 내부 | `p-4` (16px) |
| 버튼 | `px-6 py-2` |
| 인풋 필드 | `px-4 py-2` |
| 태그/뱃지 | `px-3 py-1.5` 또는 `px-2 py-0.5` |
| 네비게이션 아이템 | `px-3 py-1.5` |

### 갭
| 용도 | 값 |
|------|-----|
| 아이콘과 텍스트 | `gap-2` (8px) |
| 카드 그리드 | `gap-4` (16px) |
| 태그 목록 | `gap-1` (4px) |

---

## 테두리 (Borders)

### 색상
```css
/* Light */
border-gray-200

/* Dark */
dark:border-gray-800
```

### 두께
- 기본: `border` (1px)

---

## 모서리 반경 (Border Radius)

| 용도 | 클래스 | 값 |
|------|--------|-----|
| 카드, 인풋, 버튼, 태그 | `rounded` | 4px |
| 라운드 버튼 | `rounded-full` | 9999px |
| 바텀시트 상단 | `rounded-t-2xl` | 16px |

**중요**: `rounded-lg` 대신 `rounded` 사용 권장

---

## 아이콘 (Icons)

### 라이브러리
```typescript
import { IconName } from '@nsmr/pixelart-react'
```

### 사용 가능한 아이콘
| 아이콘 | 용도 |
|--------|------|
| `Users` | 커뮤니티 |
| `Trophy` | 랭킹 |
| `Zap` | 샘플/생성 |
| `Message` | 리뷰/메시지 |
| `Article` | 뉴스/기사 |
| `Bookmarks` | 북마크 |
| `ChartBar` | 리포트/통계 |
| `Sun` / `Moon` | 테마 토글 |
| `Reload` | 새로고침 |
| `Alert` | 경고 |
| `Download` | 다운로드 |
| `Save` | 저장 |
| `Trash` | 삭제 |
| `Close` | 닫기 |
| `Folder` | 폴더 |
| `Lock` | 비밀번호/잠금 |
| `ChevronDown` / `ChevronRight` | 접기/펼치기 |

### 아이콘 크기
| 용도 | 클래스 |
|------|--------|
| 네비게이션 | `w-[18px] h-[18px]` |
| 버튼 내부 | `w-4 h-4` |
| 빈 상태 | `w-8 h-8` |

---

## 컴포넌트 스타일

### Card
```html
<div class="card p-4">
  <!-- bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-gray-800 rounded -->
</div>
```

### Button (Primary)
```html
<button class="btn-primary">
  <!-- px-6 py-2 bg-gray-900 text-white rounded -->
  <!-- dark:bg-[#1a1a1a] dark:hover:bg-[#333333] -->
</button>
```

### Button (CTA - 그라데이션)
```html
<button class="crawl-button">
  <!-- h-[44px] 또는 h-14 (56px) -->
  <!-- 그라데이션 애니메이션 적용 -->
</button>
```

### Input
```html
<input class="form-input" />
<!-- px-4 py-2 border border-gray-300 rounded -->
<!-- dark:bg-[#1a1a1a] dark:border-gray-700 dark:text-white -->
```

### Tag/Badge
```html
<span class="inline-flex items-center gap-1 px-3 py-1.5 bg-gray-100 dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-800 rounded text-sm">
  #태그
</span>
```

### Accordion
```html
<div class="border border-gray-200 dark:border-gray-800 rounded overflow-hidden">
  <button class="w-full p-3 bg-gray-50 dark:bg-[#1a1a1a] hover:bg-gray-100 dark:hover:bg-gray-800">
    <!-- 헤더 -->
  </button>
  <div class="p-4 bg-white dark:bg-gray-900">
    <!-- 내용 -->
  </div>
</div>
```

### Navigation Item
```html
<a class="nav-item flex items-center gap-[8px]">
  <Icon class="w-[18px] h-[18px] anim-{type}" />
  <span>라벨</span>
</a>
```

---

## 애니메이션 (Animations)

### 네비게이션 아이콘 애니메이션
| 클래스 | 효과 | 용도 |
|--------|------|------|
| `anim-users` | bounce-small | 커뮤니티 |
| `anim-trophy` | tilt-shake | 랭킹 |
| `anim-sparkles` | zap-flash | 샘플/생성 |
| `anim-message` | notification-wiggle | 리뷰 |
| `anim-article` | float-up | 뉴스 |
| `anim-bookmarks` | stamp-down | 북마크 |
| `anim-chart` | scale-up-chart | 리포트 |
| `anim-theme` | spin-slow | 테마 토글 |

### 키프레임 정의
```css
/* 위아래 튀기 */
@keyframes bounce-small {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

/* 좌우 기울기 */
@keyframes tilt-shake {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(-12deg) scale(1.1); }
  50% { transform: rotate(12deg) scale(1.1); }
  75% { transform: rotate(-6deg) scale(1.05); }
  100% { transform: rotate(0deg) scale(1); }
}

/* 번개 효과 */
@keyframes zap-flash {
  0% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.2) rotate(-8deg); }
  50% { transform: scale(1.1) rotate(8deg); }
  75% { transform: scale(1.2) rotate(-5deg); }
  100% { transform: scale(1) rotate(0deg); }
}
```

---

## 반응형 브레이크포인트

| 브레이크포인트 | 값 | 설명 |
|----------------|-----|------|
| 모바일 | `max-width: 768px` | 사이드바 숨김, 햄버거 메뉴 |
| 태블릿 | `769px - 1024px` | 중간 패딩 |
| 데스크탑 | `min-width: 1025px` | 풀 사이드바 표시 |

### 모바일 주요 변경사항
- 사이드바: 슬라이드 오버레이로 변환
- 메인 콘텐츠 패딩: `px-4 py-6` (16px/24px)
- 모바일 헤더 표시 (56px 높이)

---

## UI 제작 체크리스트

새로운 UI 컴포넌트 제작 시 확인사항:

1. **색상**: Light/Dark 모드 모두 지원하는가?
2. **테두리**: `border-gray-200 dark:border-gray-800` 사용
3. **배경**: `dark:bg-[#0a0a0a]` 또는 `dark:bg-[#1a1a1a]` 사용
4. **모서리**: `rounded` (4px) 사용
5. **아이콘**: `@nsmr/pixelart-react` 사용
6. **폰트**: UI 요소는 Galmuri11, 본문은 Pretendard
7. **애니메이션**: 호버 시 적절한 애니메이션 적용
8. **반응형**: 모바일/태블릿/데스크탑 대응
