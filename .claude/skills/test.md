# /test - 테스트 실행

프론트엔드와 백엔드 테스트를 실행합니다.

---

## 사용법

```
/test [옵션]
```

### 옵션
- (기본): 전체 테스트
- `--frontend`: 프론트엔드만
- `--backend`: 백엔드만
- `--watch`: 파일 변경 감지 모드
- `--coverage`: 커버리지 리포트

---

## 프론트엔드 테스트

### 실행
```bash
cd /Users/anipen/Desktop/monitoring/frontend
npm test
```

### 커버리지
```bash
npm run test:coverage
```

### 테스트 파일 위치
```
frontend/src/
├── __tests__/           # 테스트 파일
│   ├── pages/
│   └── components/
└── setupTests.ts        # 테스트 설정
```

### 테스트 컨벤션
```tsx
// ComponentName.test.tsx
import { render, screen } from '@testing-library/react';
import { ComponentName } from './ComponentName';

describe('ComponentName', () => {
  it('should render correctly', () => {
    render(<ComponentName />);
    expect(screen.getByText('예상 텍스트')).toBeInTheDocument();
  });
});
```

---

## 백엔드 테스트

### 실행
```bash
cd /Users/anipen/Desktop/monitoring/backend
source venv/bin/activate
pytest
```

### 커버리지
```bash
pytest --cov=. --cov-report=html
```

### 테스트 파일 위치
```
backend/
├── tests/
│   ├── test_crawler/
│   ├── test_analyzer/
│   └── test_api/
└── pytest.ini
```

### 테스트 컨벤션
```python
# test_crawler_name.py
import pytest
from crawler.crawler_name import CrawlerName

class TestCrawlerName:
    @pytest.fixture
    def crawler(self):
        return CrawlerName()

    def test_crawl_success(self, crawler):
        result = crawler.crawl(max_pages=1)
        assert len(result) > 0

    def test_parse_post(self, crawler):
        html = "<div>테스트</div>"
        result = crawler._parse_post(html)
        assert result is not None
```

---

## 테스트 종류

### Unit Tests
- 개별 함수/메서드 테스트
- 빠른 실행
- 외부 의존성 모킹

### Integration Tests
- 모듈 간 상호작용 테스트
- DB 연동 테스트
- API 엔드포인트 테스트

### E2E Tests (선택)
- Playwright 사용
- 전체 사용자 플로우 테스트

---

## 모킹 예시

### 프론트엔드 (MSW)
```tsx
import { rest } from 'msw';

const handlers = [
  rest.get('/api/posts', (req, res, ctx) => {
    return res(ctx.json({ data: [] }));
  }),
];
```

### 백엔드 (pytest-mock)
```python
def test_with_mock(mocker):
    mock_response = mocker.patch('requests.get')
    mock_response.return_value.text = '<html>...</html>'

    result = crawler.fetch_page('http://example.com')
    assert result is not None
```

---

## CI/CD 통합

`.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Frontend Tests
        run: |
          cd frontend
          npm ci
          npm test

      - name: Backend Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
```

---

## 문제 해결

### 테스트 실패 디버깅
```bash
# 상세 출력
pytest -v

# 특정 테스트만
pytest tests/test_crawler.py::test_specific

# 첫 실패에서 중단
pytest -x
```
