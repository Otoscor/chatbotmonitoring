# 모니터링 프로젝트 리팩토링 기획서

**작성일**: 2026-02-26
**버전**: 1.0

---

## 1. 개요

### 1.1 목적
캐릭터 챗봇 모니터링 시스템의 코드 품질, 유지보수성, 확장성을 개선하기 위한 체계적인 리팩토링을 수행합니다.

### 1.2 범위
- **백엔드**: Python/FastAPI (크롤러, API, 분석 모듈)
- **프론트엔드**: React/TypeScript (페이지, 컴포넌트, 훅)

### 1.3 기대 효과
- 코드 중복 60% 감소
- 파일당 평균 라인 수 300줄 이하로 감소
- `any` 타입 사용 90% 제거
- 개발 생산성 향상

---

## 2. 현황 분석

### 2.1 주요 문제점 요약

| 카테고리 | 문제 수 | 우선순위 | 영향도 |
|----------|---------|----------|--------|
| 코드 중복 | 3건 | HIGH | 유지보수성 |
| 대용량 파일 | 3건 | HIGH | 가독성, 테스트 |
| 복잡한 함수 | 3건 | HIGH | 유지보수성 |
| 일관성 부재 | 3건 | HIGH | 개발 경험 |
| 타입 안전성 | 2건 | MEDIUM | 런타임 안정성 |
| 컴포넌트 구조 | 3건 | MEDIUM | 재사용성 |
| API 레이어 | 3건 | HIGH | 신뢰성 |
| 상태 관리 | 2건 | MEDIUM | 확장성 |
| 스타일링 | 3건 | LOW | 유지보수성 |

### 2.2 핵심 리팩토링 대상

#### 백엔드
| 파일 | 라인 수 | 문제 |
|------|---------|------|
| `routes.py` | 1,505줄 | 모든 API가 단일 파일에 집중 |
| `*_crawler.py` | 10개 파일 | 동일 패턴 중복 |
| API 응답 | - | 일관성 없는 에러 처리 |

#### 프론트엔드
| 파일 | 라인 수 | 문제 |
|------|---------|------|
| `CharacterSample.tsx` | 954줄 | 과도한 상태 관리, 혼합된 관심사 |
| `api.ts` | - | `any` 타입 과다 사용 |
| 컴포넌트 | - | 다크모드 처리 불일치 |

---

## 3. 리팩토링 계획

### Phase 1: 기반 구조 정립 (Critical)

#### 1.1 백엔드 - 베이스 크롤러 추출

**목표**: 10개 크롤러의 공통 로직을 베이스 클래스로 추출

**현재 상태**:
```
backend/crawler/
├── zeta_crawler.py      # 중복 코드
├── babechat_crawler.py  # 중복 코드
├── lunatalk_crawler.py  # 중복 코드
├── dcinside_crawler.py  # 중복 코드
└── ... (6개 더)
```

**목표 상태**:
```
backend/crawler/
├── base.py              # BaseCrawler 클래스
├── models.py            # 공통 데이터 모델
├── zeta_crawler.py      # BaseCrawler 상속
├── babechat_crawler.py  # BaseCrawler 상속
└── ...
```

**BaseCrawler 설계**:
```python
# backend/crawler/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import httpx
import asyncio

@dataclass
class CrawledPost:
    """공통 게시글 데이터 구조"""
    title: str
    content: Optional[str]
    url: str
    source: str
    external_id: str
    created_at: datetime

@dataclass
class CharacterData:
    """공통 캐릭터 데이터 구조"""
    name: str
    creator: Optional[str]
    description: Optional[str]
    chat_count: int
    like_count: int
    image_url: Optional[str]

class BaseCrawler(ABC):
    """모든 크롤러의 베이스 클래스"""

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 ...",
        "Accept": "text/html,application/xhtml+xml,..."
    }

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.client = httpx.AsyncClient(headers=self.DEFAULT_HEADERS)

    async def _fetch_html(self, url: str) -> str:
        """HTTP GET 요청 with 재시도"""
        return await self._retry_with_backoff(
            lambda: self.client.get(url)
        )

    async def _retry_with_backoff(
        self,
        func,
        max_retries: int = 3,
        base_delay: float = 1.0
    ):
        """지수 백오프 재시도 로직"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

    @abstractmethod
    async def crawl(self, **kwargs) -> List[CrawledPost]:
        """크롤링 실행 - 각 크롤러에서 구현"""
        pass

    @abstractmethod
    def _parse_item(self, raw_data) -> CrawledPost:
        """아이템 파싱 - 각 크롤러에서 구현"""
        pass
```

**작업 항목**:
- [ ] `backend/crawler/base.py` 생성
- [ ] `backend/crawler/models.py` 생성 (공통 데이터클래스)
- [ ] 각 크롤러 BaseCrawler 상속으로 전환
- [ ] 테스트 작성 및 검증

---

#### 1.2 백엔드 - API 라우트 분리

**목표**: 1,505줄 `routes.py`를 도메인별로 분리

**현재 상태**:
```
backend/api/
├── main.py
└── routes.py  # 1,505줄 (모든 API)
```

**목표 상태**:
```
backend/api/
├── main.py
├── schemas/
│   ├── __init__.py
│   ├── posts.py
│   ├── reports.py
│   ├── characters.py
│   └── common.py
├── routes/
│   ├── __init__.py
│   ├── posts.py        # ~170줄
│   ├── reports.py      # ~120줄
│   ├── keywords.py     # ~60줄
│   ├── crawl.py        # ~160줄
│   ├── characters.py   # ~180줄
│   ├── news.py         # ~150줄
│   ├── reviews.py      # ~185줄
│   ├── bookmarks.py    # ~205줄
│   └── samples.py      # ~90줄
└── utils/
    ├── __init__.py
    ├── response.py     # 표준 응답 래퍼
    └── date_utils.py   # 날짜 유틸리티
```

**표준 응답 래퍼**:
```python
# backend/api/utils/response.py
from pydantic import BaseModel
from typing import Optional, Any

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

def success(data: Any = None, message: str = "Success") -> dict:
    return ApiResponse(
        success=True,
        message=message,
        data=data
    ).model_dump()

def error(error: str, message: str = "Error") -> dict:
    return ApiResponse(
        success=False,
        message=message,
        error=error
    ).model_dump()
```

**작업 항목**:
- [ ] `backend/api/schemas/` 디렉토리 구조 생성
- [ ] Pydantic 모델 분리
- [ ] `backend/api/routes/` 디렉토리 구조 생성
- [ ] 도메인별 라우트 분리
- [ ] `backend/api/utils/response.py` 생성
- [ ] `backend/api/utils/date_utils.py` 생성
- [ ] `main.py`에서 라우터 통합
- [ ] 테스트 실행 및 검증

---

#### 1.3 백엔드 - 에러 처리 통일

**목표**: 모든 API 엔드포인트에서 일관된 에러 처리

**현재 문제**:
```python
# 패턴 1: dict 반환
return {"success": False, "message": "Error"}

# 패턴 2: HTTPException
raise HTTPException(status_code=404, detail="Not found")

# 패턴 3: 예외 재발생
except Exception as e:
    raise
```

**목표 패턴**:
```python
from api.utils.response import success, error

@router.get("/posts")
async def get_posts():
    try:
        posts = await fetch_posts()
        return success(data=posts, message="Posts fetched")
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

---

### Phase 2: 프론트엔드 구조 개선 (High)

#### 2.1 CharacterSample.tsx 분리

**목표**: 954줄 → 5개 파일로 분리

**현재 상태**:
```
src/pages/CharacterSample.tsx  # 954줄
```

**목표 상태**:
```
src/pages/CharacterSample/
├── index.tsx                    # ~150줄 (메인 컴포넌트)
├── components/
│   ├── TagSelector.tsx          # ~120줄
│   ├── PasswordForm.tsx         # ~80줄
│   ├── GenerationResult.tsx     # ~100줄
│   └── SavedSamplesList.tsx     # ~150줄
└── hooks/
    ├── useCharacterGeneration.ts  # ~80줄
    ├── usePasswordProtection.ts   # ~60줄
    └── useSavedSamples.ts         # ~70줄
```

**커스텀 훅 설계**:
```typescript
// hooks/useCharacterGeneration.ts
interface UseCharacterGenerationReturn {
  loading: boolean;
  error: string | null;
  result: GeneratedSample | null;
  generate: (tags: string[], password?: string) => Promise<void>;
  reset: () => void;
}

export function useCharacterGeneration(): UseCharacterGenerationReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GeneratedSample | null>(null);

  const generate = async (tags: string[], password?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.generateCharacterSample(tags, password);
      setResult(response);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return { loading, error, result, generate, reset };
}
```

**작업 항목**:
- [ ] `src/pages/CharacterSample/` 디렉토리 구조 생성
- [ ] `useCharacterGeneration` 훅 추출
- [ ] `usePasswordProtection` 훅 추출
- [ ] `useSavedSamples` 훅 추출
- [ ] 컴포넌트 분리 (TagSelector, PasswordForm, etc.)
- [ ] 메인 컴포넌트 재구성
- [ ] 기존 import 경로 업데이트

---

#### 2.2 타입 안전성 개선

**목표**: `any` 타입 90% 제거

**현재 문제** (`api.ts`):
```typescript
const params: any = { limit, days };  // line 135
const params: any = { limit };        // line 142
```

**목표 상태**:
```typescript
// types/api.ts
export interface FetchPopularPostsParams {
  limit: number;
  days: number;
  galleryId?: string;
}

export interface FetchPostsParams {
  skip: number;
  limit: number;
  source?: string;
  startDate?: string;
  endDate?: string;
}

// api.ts
const params: FetchPopularPostsParams = { limit, days };
```

**작업 항목**:
- [ ] `src/types/api.ts` 생성
- [ ] 모든 API 파라미터 인터페이스 정의
- [ ] 모든 API 응답 인터페이스 정의
- [ ] `api.ts`에서 `any` 제거
- [ ] 컴포넌트에서 `any` 제거

---

#### 2.3 다크모드 처리 통일

**목표**: 모든 컴포넌트에서 일관된 다크모드 처리

**현재 문제**:
```typescript
// 패턴 1: DOM 직접 접근
document.documentElement.classList.contains('dark')

// 패턴 2: matchMedia
window.matchMedia('(prefers-color-scheme: dark)').matches

// 패턴 3: useTheme 훅
const { isDark } = useTheme();
```

**목표 패턴**:
```typescript
// hooks/useTheme.ts (이미 존재, 확장)
export function useTheme() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // 초기화 및 변경 감지 로직
  }, []);

  const toggle = () => { /* ... */ };

  return { isDark, toggle };
}

// 모든 컴포넌트에서 사용
const { isDark } = useTheme();
const bgColor = isDark ? '#1a1a1a' : '#ffffff';
```

---

### Phase 3: 성능 및 품질 개선 (Medium)

#### 3.1 N+1 쿼리 문제 해결

**위치**: `routes.py` lines 1093-1122 (get_app_review_stats)

**현재 문제**:
```python
for app_name in app_names:  # N번 반복
    query = select(AppReview).where(AppReview.app_name == app_name)
    # N번의 쿼리 실행
```

**목표 상태**:
```python
from sqlalchemy import func

query = select(
    AppReview.app_name,
    func.count(AppReview.id).label('total_count'),
    func.avg(AppReview.rating).label('avg_rating'),
    func.max(AppReview.crawled_at).label('latest_date')
).group_by(AppReview.app_name)

result = await db.execute(query)
stats = result.all()  # 1번의 쿼리로 해결
```

---

#### 3.2 날짜 유틸리티 추출

**현재 중복 코드**:
```python
# 10곳 이상에서 반복
start_of_day = target_date.replace(hour=0, minute=0, second=0)
end_of_day = start_of_day + timedelta(days=1)
```

**목표**:
```python
# backend/api/utils/date_utils.py
def get_day_boundaries(date: datetime) -> tuple[datetime, datetime]:
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end

def filter_by_date(query, column, date: datetime):
    start, end = get_day_boundaries(date)
    return query.where(column >= start, column < end)
```

---

#### 3.3 상태 관리 개선

**현재 문제** (AppReviews.tsx):
```typescript
// 7개의 개별 useState
const [reviews, setReviews] = useState([]);
const [stats, setStats] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
// ... 더 많은 상태
```

**목표**:
```typescript
// hooks/useAppReviews.ts
interface AppReviewsState {
  reviews: AppReview[];
  stats: AppReviewStats | null;
  loading: boolean;
  error: string | null;
  selectedApp: string | null;
}

export function useAppReviews() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const fetchReviews = async () => { /* ... */ };
  const fetchStats = async () => { /* ... */ };
  const selectApp = (app: string) => { /* ... */ };

  return { ...state, fetchReviews, fetchStats, selectApp };
}
```

---

### Phase 4: 정리 및 최적화 (Low)

#### 4.1 데드 코드 제거

**대상**:
- `routes.py` lines 1302-1308: 주석 처리된 AI 요약 기능
- `routes.py` lines 1400-1405: 비활성화된 엔드포인트

**작업**: 완전히 제거하고 Git 히스토리에만 보존

---

#### 4.2 하드코딩 값 설정 파일로 이동

**현재**:
```typescript
// CharacterSample.tsx
const DAILY_LIMIT = 50;  // 하드코딩
```

**목표**:
```typescript
// config/constants.ts
export const CHARACTER_SAMPLE = {
  DAILY_LIMIT: 50,
  MAX_TAGS: 10,
  PASSWORD_LENGTH: 4,
} as const;
```

---

#### 4.3 스타일 정리

**작업 항목**:
- [ ] 인라인 스타일 → CSS 클래스로 이동
- [ ] 중복 Tailwind 클래스 → @apply 지시문
- [ ] 애니메이션 키프레임 별도 파일로 분리

---

## 4. 일정 계획

| Phase | 작업 | 예상 기간 | 담당 |
|-------|------|----------|------|
| **Phase 1** | 기반 구조 정립 | - | - |
| 1.1 | 베이스 크롤러 추출 | - | Backend |
| 1.2 | API 라우트 분리 | - | Backend |
| 1.3 | 에러 처리 통일 | - | Backend |
| **Phase 2** | 프론트엔드 구조 개선 | - | - |
| 2.1 | CharacterSample 분리 | - | Frontend |
| 2.2 | 타입 안전성 개선 | - | Frontend |
| 2.3 | 다크모드 통일 | - | Frontend |
| **Phase 3** | 성능 및 품질 개선 | - | - |
| 3.1 | N+1 쿼리 해결 | - | Backend |
| 3.2 | 날짜 유틸리티 추출 | - | Backend |
| 3.3 | 상태 관리 개선 | - | Frontend |
| **Phase 4** | 정리 및 최적화 | - | - |
| 4.1-4.3 | 데드코드, 설정, 스타일 | - | Full Stack |

---

## 5. 리스크 및 대응

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|----------|
| 기존 기능 장애 | HIGH | 각 단계별 테스트 필수 실행 |
| 일정 지연 | MEDIUM | Phase별 독립 배포 가능하게 설계 |
| 충돌 발생 | MEDIUM | 작은 단위로 PR 생성 및 리뷰 |

---

## 6. 성공 지표

| 지표 | 현재 | 목표 |
|------|------|------|
| routes.py 라인 수 | 1,505 | < 100 (라우터 등록만) |
| CharacterSample.tsx 라인 수 | 954 | < 200 |
| `any` 타입 사용 | 15+ 곳 | < 2곳 |
| 크롤러 중복 코드 | 70% | < 20% |
| 평균 파일 라인 수 | 400+ | < 300 |

---

## 7. 참고 자료

- [리팩토링 스킬](/refactor)
- [디자인 시스템](./skills.md)
- [vive-md](https://github.com/johunsang/vive-md)
