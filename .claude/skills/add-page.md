# /add-page - 새 프론트엔드 페이지 추가

새로운 페이지 컴포넌트를 프론트엔드에 추가합니다.

---

## 사용법

```
/add-page <페이지명> <라우트경로>
```

### 예시
```
/add-page Statistics /statistics
```

---

## 페이지 생성 가이드

### 1. 페이지 파일 생성

위치: `frontend/src/pages/{페이지명}.tsx`

### 2. 기본 템플릿

```tsx
import React, { useState, useEffect } from 'react';
import { ChartBar } from '@nsmr/pixelart-react';

interface {페이지명}Data {
  // 데이터 타입 정의
}

const {페이지명}: React.FC = () => {
  const [data, setData] = useState<{페이지명}Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // TODO: 데이터 fetching 로직
      // const response = await api.get{페이지명}Data();
      // setData(response);
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">{error}</p>
        <button
          onClick={fetchData}
          className="mt-4 px-4 py-2 bg-gray-900 text-white rounded dark:bg-[#1a1a1a]"
        >
          다시 시도
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 페이지 헤더 */}
      <div className="flex items-center gap-3">
        <ChartBar className="w-6 h-6" />
        <h1 className="text-2xl font-bold font-galmuri">{페이지명}</h1>
      </div>

      {/* 컨텐츠 영역 */}
      <div className="card p-4">
        {/* TODO: 페이지 컨텐츠 */}
      </div>
    </div>
  );
};

export default {페이지명};
```

---

### 3. 라우터에 등록

`frontend/src/App.tsx` 수정:

```tsx
import {페이지명} from './pages/{페이지명}';

// Routes 내부에 추가
<Route path="/{라우트경로}" element={<{페이지명} />} />
```

---

### 4. 네비게이션에 추가

`frontend/src/components/Layout.tsx` 수정:

```tsx
const navItems = [
  // ... 기존 항목들
  {
    path: '/{라우트경로}',
    label: '{페이지명}',
    icon: ChartBar,  // 적절한 아이콘 선택
    animClass: 'anim-chart'
  },
];
```

---

## 사용 가능한 아이콘

```tsx
import {
  Users,       // 커뮤니티
  Trophy,      // 랭킹
  Zap,         // 샘플/생성
  Message,     // 리뷰/메시지
  Article,     // 뉴스/기사
  Bookmarks,   // 북마크
  ChartBar,    // 리포트/통계
} from '@nsmr/pixelart-react';
```

---

## 디자인 시스템 참고

새 페이지 작성 시 `.claude/skills.md`의 디자인 시스템을 따르세요:

- **카드**: `card p-4` 클래스 사용
- **배경**: Light `bg-white`, Dark `dark:bg-[#0a0a0a]`
- **테두리**: `border-gray-200 dark:border-gray-800`
- **모서리**: `rounded` (4px)
- **폰트**: UI는 Galmuri11, 본문은 Pretendard

---

## 체크리스트

- [ ] 페이지 컴포넌트 생성 (`pages/{페이지명}.tsx`)
- [ ] 라우터에 등록 (`App.tsx`)
- [ ] 네비게이션에 추가 (`Layout.tsx`)
- [ ] 데이터 API 연결 (`utils/api.ts`)
- [ ] Light/Dark 모드 테스트
- [ ] 모바일 반응형 테스트
