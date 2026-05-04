# /crawl - 웹 크롤러 실행

웹 크롤링을 실행하여 커뮤니티 데이터를 수집합니다.

---

## 사용법

```
/crawl [크롤러명]
```

### 인자
- `크롤러명` (선택): 특정 크롤러만 실행. 생략 시 전체 실행
  - `dcinside` - 디시인사이드 (글쓰는AI, AI채팅)
  - `arcalive` - 아카라이브
  - `zeta` - 제타 캐릭터
  - `babechat` - 베이브챗 캐릭터
  - `lunatalk` - 루나톡 캐릭터
  - `news` - 구글 뉴스 RSS
  - `reviews` - 앱 리뷰

---

## 실행 순서

1. **환경 확인**
   ```bash
   cd /Users/anipen/Desktop/monitoring/backend
   source venv/bin/activate  # 가상환경 활성화
   ```

2. **크롤러 실행**
   - 전체 실행: `python -m crawler.run_all`
   - 개별 실행: `python -m crawler.{크롤러명}_crawler`

3. **결과 확인**
   - 성공/실패 건수 출력
   - 에러 발생 시 로그 확인: `backend/logs/`

---

## 크롤러 파일 위치

| 크롤러 | 파일 |
|--------|------|
| 디시인사이드 | `backend/crawler/dcinside_crawler.py` |
| 아카라이브 | `backend/crawler/arcalive_crawler.py` |
| 제타 | `backend/crawler/zeta_crawler.py` |
| 베이브챗 | `backend/crawler/babechat_crawler.py` |
| 루나톡 | `backend/crawler/lunatalk_crawler.py` |
| 구글뉴스 | `backend/crawler/google_news_crawler.py` |
| 앱리뷰 | `backend/crawler/app_review_crawler.py` |

---

## 주의사항

- 크롤링은 각 사이트의 robots.txt 및 이용약관을 준수합니다
- 과도한 요청을 방지하기 위해 딜레이가 적용되어 있습니다
- Playwright 크롤러는 헤드리스 브라우저가 필요합니다
