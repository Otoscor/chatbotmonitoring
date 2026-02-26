# /refactor - 코드 리팩토링 가이드

코드 품질 개선과 리팩토링 작업을 수행합니다.

---

## 사용법

```
/refactor [대상] [옵션]
```

### 대상
- `backend` - 백엔드 리팩토링
- `frontend` - 프론트엔드 리팩토링
- `crawler` - 크롤러 모듈 리팩토링
- `api` - API 레이어 리팩토링
- `types` - 타입 안전성 개선

### 옵션
- `--dry-run` - 변경 없이 분석만
- `--phase <1-4>` - 특정 페이즈만 실행

---

## 리팩토링 원칙

### 1. DRY (Don't Repeat Yourself)
- 중복 코드 추출 → 공통 함수/클래스
- 3번 이상 반복되면 추상화 고려

### 2. SRP (Single Responsibility Principle)
- 파일당 300줄 이하 유지
- 함수당 하나의 책임

### 3. 일관성 (Consistency)
- 동일한 패턴은 동일한 방식으로
- 에러 처리, 응답 형식 통일

### 4. 타입 안전성 (Type Safety)
- `any` 타입 제거
- 명시적 인터페이스 정의

---

## 백엔드 리팩토링 패턴

### 베이스 크롤러 추출
```python
# backend/crawler/base_crawler.py
class BaseCrawler:
    def __init__(self):
        self.headers = {"User-Agent": "..."}

    async def _fetch_html(self, url: str) -> str:
        """공통 HTTP 요청 로직"""
        pass

    async def _retry_with_backoff(self, func, max_retries=3):
        """공통 재시도 로직"""
        pass
```

### API 라우트 분리
```
backend/api/
├── routes/
│   ├── __init__.py
│   ├── posts.py
│   ├── reports.py
│   ├── keywords.py
│   ├── characters.py
│   ├── news.py
│   ├── reviews.py
│   └── bookmarks.py
├── schemas.py      # Pydantic 모델
└── main.py
```

### 표준 응답 래퍼
```python
# backend/api/response.py
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
    error: Optional[str] = None

def success_response(data, message="Success"):
    return ApiResponse(success=True, message=message, data=data)

def error_response(error, message="Error"):
    return ApiResponse(success=False, message=message, error=str(error))
```

---

## 프론트엔드 리팩토링 패턴

### 커스텀 훅 추출
```typescript
// hooks/useCharacterGeneration.ts
export function useCharacterGeneration() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = async (tags: string[]) => {
    // 생성 로직
  };

  return { loading, error, generate };
}
```

### 타입 정의 중앙화
```typescript
// types/api.ts
export interface Post {
  id: number;
  title: string;
  source: string;
  created_at: string;
}

export interface FetchPostsParams {
  skip: number;
  limit: number;
  source?: string;
}
```

### 컴포넌트 분리
```
src/pages/CharacterSample/
├── index.tsx              # 메인 컴포넌트
├── components/
│   ├── TagSelector.tsx
│   ├── PasswordForm.tsx
│   └── SavedSamples.tsx
└── hooks/
    ├── useGeneration.ts
    └── usePasswordProtection.ts
```

---

## 체크리스트

### 리팩토링 전
- [ ] 테스트 커버리지 확인
- [ ] 현재 동작 스크린샷/기록
- [ ] Git 브랜치 생성

### 리팩토링 중
- [ ] 작은 단위로 커밋
- [ ] 기존 테스트 통과 확인
- [ ] 타입 에러 없음 확인

### 리팩토링 후
- [ ] 전체 테스트 실행
- [ ] 기능 동작 확인
- [ ] 코드 리뷰 요청

---

## 참고 문서

- [리팩토링 기획서](./REFACTORING_PLAN.md)
- [디자인 시스템](../skills.md)
