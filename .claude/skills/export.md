# /export - 데이터 JSON 내보내기

SQLite 데이터베이스의 데이터를 프론트엔드용 JSON 파일로 내보냅니다.

---

## 사용법

```
/export [옵션]
```

### 옵션
- `--all` (기본): 모든 데이터 내보내기
- `--posts`: 게시글 데이터만
- `--characters`: 캐릭터 랭킹만
- `--keywords`: 키워드 데이터만
- `--news`: 뉴스 데이터만
- `--reviews`: 앱 리뷰만
- `--reports`: 일일 리포트만

---

## 실행 순서

1. **환경 확인**
   ```bash
   cd /Users/anipen/Desktop/monitoring/backend
   source venv/bin/activate
   ```

2. **내보내기 실행**
   ```bash
   python export_data.py
   ```

3. **출력 파일 확인**
   - 위치: `frontend/public/data/`
   - 파일 목록:
     - `posts.json` - 게시글 목록
     - `character_rankings.json` - 캐릭터 랭킹
     - `keywords.json` - 키워드 분석
     - `news.json` - 뉴스 기사
     - `app_reviews.json` - 앱 리뷰
     - `daily_reports.json` - 일일 리포트
     - `chat_services.json` - 챗봇 서비스별 캐릭터

---

## 내보내기 스크립트

| 파일 | 설명 |
|------|------|
| `backend/export_data.py` | 메인 내보내기 스크립트 |
| `backend/models/database.py` | SQLAlchemy 모델 정의 |

---

## JSON 파일 구조

### posts.json
```json
{
  "updated_at": "2024-01-01T00:00:00",
  "total_count": 1234,
  "data": [
    {
      "id": 1,
      "title": "제목",
      "source": "dcinside",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### character_rankings.json
```json
{
  "updated_at": "2024-01-01T00:00:00",
  "rankings": [
    {
      "rank": 1,
      "name": "캐릭터명",
      "mention_count": 100,
      "trend": "up"
    }
  ]
}
```

---

## 주의사항

- 내보내기 전 크롤링이 완료되었는지 확인하세요
- JSON 파일은 Git에 커밋되어 GitHub Pages로 배포됩니다
- 대용량 데이터는 페이지네이션 처리가 필요할 수 있습니다
