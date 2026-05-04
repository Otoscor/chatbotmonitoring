# 🔧 문제 해결 가이드

## 발생한 문제

### 증상
- 프론트엔드에서 500 Internal Server Error 발생
- `/api/reports/latest`, `/api/characters/ranking` 등 모든 API 호출 실패

### 에러 로그
```
:3000/api/reports/latest:1  Failed to load resource: the server responded with a status of 500 (Internal Server Error)
:3000/api/characters/ranking?days=7&limit=10:1  Failed to load resource: the server responded with a status of 500 (Internal Server Error)
```

---

## 원인 분석

### 1차 원인: 데이터베이스 초기화
- 기존 데이터베이스 파일 삭제로 인해 데이터가 비어있음
- 리포트가 없는 상태에서 API 호출 시 404 에러 발생

### 2차 원인: API 응답 필드명 불일치
- **백엔드 응답**: `name`, `total_mentions`
- **프론트엔드 기대값**: `character_name`, `mention_count`
- 필드명이 달라서 데이터가 제대로 매핑되지 않음

---

## 해결 방법

### ✅ 해결 1: 크롤링 실행
데이터베이스가 비어있으면 크롤링을 먼저 실행해야 합니다.

```bash
# 백엔드 API를 통한 크롤링
curl -X POST http://localhost:8001/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"pages": 2}'

# 리포트 생성
curl -X POST http://localhost:8001/api/reports/generate
```

**결과**: 281개 게시글 수집 완료
- 뤼튼 마이너갤: 100개
- AI챗팅 마이너갤: 100개
- 아카라이브 캐릭터AI: 81개

### ✅ 해결 2: 프론트엔드 API 필드명 수정

**변경 전:**
```typescript
// Dashboard.tsx, Characters.tsx
items={characterRanking?.map((c: any, idx: number) => ({
  rank: idx + 1,
  name: c.character_name,      // ❌ 잘못된 필드명
  score: c.mention_count        // ❌ 잘못된 필드명
})) || []}
```

**변경 후:**
```typescript
items={characterRanking?.map((c: any, idx: number) => ({
  rank: idx + 1,
  name: c.name,                 // ✅ 올바른 필드명
  score: c.total_mentions       // ✅ 올바른 필드명
})) || []}
```

---

## API 응답 구조

### `/api/characters/ranking`
```json
[
  {
    "name": "필독",
    "total_mentions": 2,
    "rank": 1
  }
]
```

### `/api/reports/latest`
```json
{
  "id": 1,
  "report_date": "2026-01-14T16:46:08",
  "total_posts": 281,
  "total_views": 136117,
  "total_recommends": 648,
  "total_comments": 1507,
  "top_keywords": [...],
  "top_characters": [
    {
      "name": "필독",
      "mentions": 2,
      "rank": 1
    }
  ]
}
```

---

## 크롤링 작동 확인

### 테스트 결과
```bash
# 크롤링 테스트
$ python3 backend/crawler/multi_crawler.py

✅ [뤼튼 마이너갤] 100개 수집 완료
✅ [AI챗팅 마이너갤] 100개 수집 완료
✅ [아카라이브 캐릭터AI] 81개 수집 완료

총 281개 게시글 수집 (약 30초 소요)
```

---

## 기존 vs 현재 차이점

| 항목 | 기존 (programming 갤러리) | 현재 (3개 사이트) |
|------|--------------------------|-------------------|
| **크롤러** | DCInsideCrawler 단일 | multi_crawler (통합) |
| **대상** | 1개 갤러리 | 3개 갤러리/채널 |
| **구조** | 일반 갤러리 | 마이너갤 2개 + 아카라이브 1개 |
| **크롤러 타입** | dcinside_crawler.py | dcinside_crawler.py + arcalive_crawler.py |

### 주요 변경 사항
1. **config.py**: `target_gallery_id` → `target_galleries` (리스트)
2. **크롤러**: 단일 크롤러 → multi_crawler 통합 시스템
3. **API**: 동일한 엔드포인트, 내부 로직만 변경

---

## 예방 조치

### 1. 초기 데이터 확인
시스템 시작 시 항상 데이터 존재 여부 확인:

```bash
curl http://localhost:8001/api/reports/latest
```

- **404 응답**: 크롤링 필요
- **200 응답**: 정상 작동

### 2. 필드명 일치 확인
API 응답과 프론트엔드 모델이 일치하는지 확인:
- TypeScript 인터페이스와 백엔드 Pydantic 모델 비교
- 테스트 코드 작성 권장

### 3. 에러 핸들링 개선
프론트엔드에서 404 에러 발생 시 사용자에게 크롤링 안내 표시

---

## 체크리스트

시스템 정상 작동 확인:

- [✅] 백엔드 실행 중 (`http://localhost:8001`)
- [✅] 프론트엔드 실행 중 (`http://localhost:3000`)
- [✅] 데이터베이스 존재 (`monitoring.db`)
- [✅] 최소 1개 이상의 리포트 존재
- [✅] 크롤러 정상 작동 (281개 수집)
- [✅] API 필드명 일치
- [✅] 프론트엔드 데이터 표시 정상

---

## 문제 발생 시 순서

1. **백엔드 로그 확인**
   ```bash
   # 터미널에서 실행 중인 백엔드 로그 확인
   ```

2. **API 직접 테스트**
   ```bash
   curl http://localhost:8001/api/reports/latest
   ```

3. **데이터베이스 확인**
   ```bash
   ls -lh backend/api/monitoring.db
   ```

4. **크롤링 재실행**
   ```bash
   curl -X POST http://localhost:8001/api/crawl -d '{"pages": 2}'
   curl -X POST http://localhost:8001/api/reports/generate
   ```

5. **브라우저 새로고침**
   - 캐시 삭제 후 재접속

---

**마지막 업데이트**: 2026-01-14  
**해결 상태**: ✅ 완료
