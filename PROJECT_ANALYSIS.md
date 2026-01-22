# 캐릭터 챗봇 모니터링 시스템 - 프로젝트 분석 리포트

## 📋 프로젝트 개요

### 프로젝트명
**캐릭터 챗봇 모니터링 시스템 (Chatbot Monitoring System)**

### 목적
캐릭터 챗봇 커뮤니티의 동향을 자동으로 수집하고 분석하여, 인기 트렌드와 키워드를 시각화하는 웹 애플리케이션입니다.

### 배포 정보
- **GitHub Pages**: https://otoscor.github.io/chatbotmonitoring/
- **저장소**: https://github.com/Otoscor/chatbotmonitoring

---

## 🏗️ 아키텍처

### 전체 구조
```
로컬 환경 (관리자)
    ↓
크롤링 실행 → 데이터 수집 → SQLite DB 저장
    ↓
JSON Export → GitHub 푸시
    ↓
GitHub Actions 자동 빌드
    ↓
GitHub Pages 배포
    ↓
사용자 접속 (정적 사이트)
```

### 특징
- **정적 사이트 배포 방식**: 완전 무료(GitHub Pages), CDN을 통한 빠른 로딩
- **백엔드는 로컬 전용**: 크롤링과 분석은 로컬에서 실행, 결과만 JSON으로 export
- **서버리스 구조**: 서버 관리 불필요, 자동 배포

---

## 📁 프로젝트 구조

### 디렉토리 구성
```
monitoring/
├── backend/               # 백엔드 (로컬 전용)
│   ├── api/              # FastAPI 서버 (개발용)
│   ├── crawler/          # 크롤링 모듈
│   │   ├── dcinside_crawler.py
│   │   ├── arcalive_crawler.py
│   │   ├── zeta_crawler.py
│   │   ├── babechat_crawler.py
│   │   ├── lunatalk_crawler.py
│   │   ├── crack_crawler.py
│   │   └── multi_crawler.py (통합 크롤러)
│   ├── analyzer/         # 데이터 분석 모듈
│   │   ├── keyword_extractor.py
│   │   ├── character_ranker.py
│   │   └── trend_analyzer.py
│   ├── models/           # 데이터베이스 모델
│   │   └── database.py
│   ├── scheduler/        # 자동 실행 스케줄러
│   ├── config.py         # 설정 파일
│   ├── export_data.py    # JSON export 스크립트
│   └── monitoring.db     # SQLite 데이터베이스
│
├── frontend/             # 프론트엔드
│   ├── public/
│   │   └── data/        # JSON 데이터 파일
│   ├── src/
│   │   ├── components/  # React 컴포넌트
│   │   │   ├── Layout.tsx
│   │   │   ├── StatCard.tsx
│   │   │   ├── KeywordCloud.tsx
│   │   │   └── RankingList.tsx
│   │   ├── pages/       # 페이지
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Reports.tsx
│   │   │   ├── ReportDetail.tsx
│   │   │   ├── CharacterRankings.tsx
│   │   │   ├── Keywords.tsx
│   │   │   └── News.tsx
│   │   ├── hooks/       # 커스텀 훅
│   │   │   └── useApi.ts
│   │   ├── utils/       # 유틸리티
│   │   │   └── api.ts
│   │   └── App.tsx      # 메인 앱
│   └── package.json
│
└── .github/
    └── workflows/
        └── deploy.yml   # GitHub Actions 배포 설정
```

---

## 🛠️ 기술 스택

### 백엔드
| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 프로그래밍 언어 |
| FastAPI | 0.109.0 | 웹 API 서버 (개발용) |
| SQLAlchemy | 2.0.25 | ORM |
| SQLite | - | 데이터베이스 |
| BeautifulSoup4 | 4.12.3 | HTML 파싱 |
| Playwright | 1.41.0 | 브라우저 자동화 |
| scikit-learn | 1.4.0 | 데이터 분석 |
| pandas | 2.2.0 | 데이터 처리 |

### 프론트엔드
| 기술 | 버전 | 용도 |
|------|------|------|
| React | 18.2.0 | UI 라이브러리 |
| TypeScript | 5.2.2 | 타입 안정성 |
| Vite | 5.0.8 | 빌드 도구 |
| TailwindCSS | 3.4.0 | 스타일링 |
| Recharts | 2.10.3 | 차트 라이브러리 |
| React Router | 6.21.0 | 라우팅 |
| Axios | 1.6.5 | HTTP 클라이언트 |

### 배포
- **GitHub Pages**: 프론트엔드 호스팅
- **GitHub Actions**: 자동 CI/CD

---

## 🗄️ 데이터베이스 스키마

### 1. posts (게시글)
```python
- id: 고유 번호
- post_id: 원본 게시글 ID (unique)
- gallery_id: 게시판 ID
- title: 제목
- author: 작성자
- created_at: 작성 시간
- crawled_at: 크롤링 시간
- view_count: 조회수
- recommend_count: 추천수
- comment_count: 댓글수
- url: 원본 링크
```

### 2. post_keywords (게시글 키워드)
```python
- id: 고유 번호
- post_id: 게시글 ID (FK)
- keyword: 키워드
- score: TF-IDF 점수
```

### 3. daily_reports (일일 리포트)
```python
- id: 고유 번호
- report_date: 리포트 날짜
- total_posts: 총 게시글 수
- total_views: 총 조회수
- total_recommends: 총 추천수
- total_comments: 총 댓글수
- top_keywords: 인기 키워드 (JSON)
- top_characters: 인기 캐릭터 (JSON)
- sentiment_summary: 감정 분석 (JSON)
- trending_topics: 트렌딩 토픽 (JSON)
```

### 4. character_mentions (캐릭터 언급)
```python
- id: 고유 번호
- character_name: 캐릭터 이름
- mention_date: 언급 날짜
- mention_count: 언급 횟수
- source_gallery: 출처 게시판
```

### 5. chat_service_characters (챗봇 서비스 캐릭터)
```python
- id: 고유 번호
- service: 서비스명 (zeta, babechat, lunatalk, crack)
- character_id: 서비스 내 고유 ID
- rank: 순위
- name: 캐릭터 이름
- author: 제작자
- views: 조회수
- tags: 태그 목록 (JSON)
- description: 설명
- thumbnail_url: 썸네일 URL
- character_url: 캐릭터 URL
- crawled_at: 크롤링 시간
```

### 6. news_articles (뉴스 기사)
```python
- id: 고유 번호
- article_id: 기사 ID (unique)
- source: 출처 (naver, google)
- title: 제목
- description: 설명
- url: 기사 URL
- publisher: 언론사명
- published_at: 발행일
- crawled_at: 크롤링 시간
- keyword: 검색 키워드
```

---

## 🕷️ 크롤링 대상 사이트

### 커뮤니티 게시판
1. **뤼튼 마이너갤러리** (디시인사이드)
   - URL: https://gall.dcinside.com/mgallery/board/lists/?id=wrtnai
   - 활동량: 높음

2. **AI챗팅 마이너갤러리** (디시인사이드)
   - URL: https://gall.dcinside.com/mgallery/board/lists/?id=aichatting
   - 활동량: 높음

3. **캐릭터AI** (아카라이브)
   - URL: https://arca.live/b/characterai
   - 활동량: 보통

### 캐릭터 챗봇 서비스
4. **Zeta** (제타)
5. **Babechat** (베이브챗)
6. **Lunatalk** (루나톡)
7. **Crack** (크랙)

---

## 🔧 주요 기능 모듈

### 1. 크롤러 모듈 (`backend/crawler/`)

#### multi_crawler.py
- **역할**: 모든 크롤러를 통합 실행
- **기능**: 설정된 모든 갤러리/게시판을 순차적으로 크롤링
- **특징**: Rate limiting (사이트 간 2초 딜레이)

#### dcinside_crawler.py
- **대상**: 디시인사이드 갤러리
- **지원**: 일반갤러리, 마이너갤러리

#### arcalive_crawler.py
- **대상**: 아카라이브 채널

#### zeta_crawler.py, babechat_crawler.py, lunatalk_crawler.py, crack_crawler.py
- **대상**: 각 캐릭터 챗봇 서비스
- **수집 데이터**: 캐릭터 순위, 이름, 조회수, 태그 등

### 2. 분석 모듈 (`backend/analyzer/`)

#### keyword_extractor.py
- **기능**: 게시글에서 키워드 추출
- **방법**: TF-IDF 알고리즘

#### character_ranker.py
- **기능**: 캐릭터 언급 빈도 분석
- **출력**: 인기 캐릭터 순위

#### trend_analyzer.py
- **기능**: 일일 리포트 생성
- **분석**: 통계, 트렌드, 인기 키워드/캐릭터

### 3. API 엔드포인트 (`backend/api/routes.py`)

#### 게시글 관련
- `GET /api/posts`: 게시글 목록 조회
- `GET /api/posts/popular`: 인기 게시글 조회
- `GET /api/posts/{post_id}`: 특정 게시글 조회
- `GET /api/posts/stats/daily`: 일일 통계 조회

#### 리포트 관련
- `GET /api/reports`: 리포트 목록 조회
- `GET /api/reports/latest`: 최신 리포트 조회
- `GET /api/reports/{date}`: 특정 날짜 리포트 조회
- `GET /api/reports/{date}/keywords`: 해당 날짜 인기 키워드
- `GET /api/reports/{date}/characters`: 해당 날짜 인기 캐릭터

#### 키워드/캐릭터 관련
- `GET /api/keywords/trending`: 트렌딩 키워드
- `GET /api/characters/ranking`: 캐릭터 순위
- `GET /api/characters/chat-services`: 챗봇 서비스별 캐릭터

#### 크롤링 관련
- `POST /api/crawl/trigger`: 수동 크롤링 트리거
- `POST /api/reports/generate`: 수동 리포트 생성

---

## 🎨 디자인 시스템

### 디자인 철학
- **Notion 스타일**: 미니멀리즘
- **컬러**: 그레이스케일 전용 (컬러 사용 금지)
- **타이포그래피**: 일관된 서체 및 크기
- **여백**: 충분한 간격으로 가독성 확보

### 컬러 팔레트
```css
gray-50:  #FAFAFA  /* 배경 */
gray-200: #EEEEEE  /* 테두리 */
gray-400: #BDBDBD  /* 비활성 */
gray-600: #757575  /* 일반 텍스트 */
gray-900: #212121  /* 주요 텍스트 */
```

### 금지 사항
- ❌ 이모티콘 사용 금지
- ❌ 컬러 사용 금지 (그레이스케일만)
- ❌ 과도한 애니메이션 금지

---

## 📊 프론트엔드 페이지 구성

### 1. Dashboard (`/`)
- **기능**: 전체 현황 한눈에 보기
- **콘텐츠**: 통계 카드, 인기 게시글, 트렌드 차트

### 2. Reports (`/reports`)
- **기능**: 날짜별 분석 리포트 목록
- **기능**: 리포트 검색 및 필터링

### 3. Report Detail (`/reports/:date`)
- **기능**: 특정 날짜의 상세 분석
- **콘텐츠**: 인기 키워드, 캐릭터 순위, 트렌드

### 4. Character Rankings (`/character-rankings`)
- **기능**: 캐릭터 인기 순위 표시
- **콘텐츠**: TOP 캐릭터, 챗봇 서비스별 순위

### 5. News (`/news`)
- **기능**: AI 챗봇 관련 뉴스 기사
- **출처**: 구글 뉴스, 네이버 뉴스

---

## 🚀 배포 및 업데이트 프로세스

### 원클릭 업데이트
```bash
./update_site.sh
```

이 스크립트는:
1. 데이터를 JSON으로 export
2. Git 커밋 및 푸시
3. GitHub Actions 자동 배포

### 수동 업데이트
```bash
# 1. 데이터 Export
cd backend
python export_data.py

# 2. Git 커밋 및 푸시
git add frontend/public/data/
git commit -m "chore: 데이터 업데이트"
git push origin main
```

### GitHub Actions
- `main` 브랜치에 푸시 시 자동 빌드
- Vite로 프론트엔드 빌드
- GitHub Pages에 자동 배포

---

## 🔑 환경 변수

### 로컬 개발 (frontend/.env)
```bash
VITE_API_URL=http://localhost:8001/api
VITE_USE_STATIC_DATA=false
```

### 프로덕션 (배포용)
```bash
VITE_USE_STATIC_DATA=true
```

---

## 📝 주요 설정 파일

### backend/config.py
```python
- database_url: SQLite 경로
- crawl_delay_seconds: 크롤링 딜레이 (1.5초)
- max_pages_per_crawl: 페이지당 크롤링 수 (3페이지)
- target_galleries: 크롤링 대상 목록
```

### frontend/package.json
```json
- scripts:
  - dev: 개발 서버 실행
  - build: 프로덕션 빌드
  - preview: 빌드 결과 미리보기
```

---

## 🔄 데이터 흐름

```
1. 크롤러 실행
   ↓
2. 게시글/캐릭터 데이터 수집
   ↓
3. SQLite DB에 저장
   ↓
4. 분석기 실행 (키워드 추출, 캐릭터 순위 계산)
   ↓
5. 일일 리포트 생성
   ↓
6. JSON Export (export_data.py)
   ↓
7. GitHub 푸시
   ↓
8. GitHub Actions 빌드
   ↓
9. GitHub Pages 배포
   ↓
10. 사용자 접속 및 데이터 조회
```

---

## 🎯 핵심 특징

1. **완전 무료**: GitHub Pages를 활용한 무료 호스팅
2. **서버리스**: 백엔드 서버 불필요, 정적 사이트만 배포
3. **자동화**: 크롤링 → 분석 → 배포 자동화
4. **확장 가능**: 새로운 사이트 추가 용이
5. **빠른 속도**: CDN을 통한 빠른 로딩
6. **깔끔한 UI**: Notion 스타일의 미니멀 디자인

---

## 🔍 데이터 수집 및 분석

### 수집 주기
- 수동 실행 또는 스케줄러 설정

### 크롤링 설정
- **딜레이**: 1.5초 (사이트 부하 방지)
- **페이지 수**: 3페이지
- **재시도**: 최대 3회

### 분석 항목
- 인기 키워드 (TF-IDF)
- 캐릭터 언급 빈도
- 트렌드 변화
- 게시판별 통계

---

## ⚠️ 주의사항

### 크롤링
- Rate Limiting 준수 (사이트 간 2초 딜레이)
- robots.txt 준수
- 공개 게시글만 수집
- 개인정보 수집 없음

### 배포
- 정적 데이터 모드 사용 (`VITE_USE_STATIC_DATA=true`)
- JSON 파일 크기 최적화 필요
- 캐시 정책 고려

---

## 📚 문서 파일

- [README.md](file:///Users/anipen/Desktop/monitoring/README.md): 프로젝트 소개 및 시작 가이드
- [PROJECT_GUIDE.md](file:///Users/anipen/Desktop/monitoring/PROJECT_GUIDE.md): 초보자용 완전 정복 가이드
- [CRAWLING_TARGETS.md](file:///Users/anipen/Desktop/monitoring/CRAWLING_TARGETS.md): 크롤링 대상 사이트 목록
- [DESIGN_SYSTEM.md](file:///Users/anipen/Desktop/monitoring/DESIGN_SYSTEM.md): 디자인 시스템 가이드
- [DEPLOYMENT.md](file:///Users/anipen/Desktop/monitoring/DEPLOYMENT.md): 배포 가이드 (Render, Vercel)
- [TROUBLESHOOTING.md](file:///Users/anipen/Desktop/monitoring/TROUBLESHOOTING.md): 문제 해결 가이드

---

## 🎓 학습 및 이해를 위한 핵심 개념

### 1. 크롤링 (Crawling)
웹사이트를 자동으로 탐색하여 데이터를 수집하는 기술입니다.

### 2. API (Application Programming Interface)
프로그램 간 데이터 통신을 위한 인터페이스입니다.

### 3. ORM (Object-Relational Mapping)
객체와 데이터베이스 테이블을 매핑하는 기술입니다.

### 4. TF-IDF (Term Frequency-Inverse Document Frequency)
문서 내 키워드의 중요도를 계산하는 알고리즘입니다.

### 5. 정적 사이트 (Static Site)
서버 없이 HTML/CSS/JS 파일만으로 동작하는 웹사이트입니다.

---

## 🔮 향후 개선 가능한 부분

1. **실시간 크롤링**: 스케줄러를 통한 자동 크롤링
2. **감정 분석**: 게시글의 긍정/부정 분석
3. **알림 기능**: 특정 키워드 감지 시 알림
4. **대시보드 커스터마이징**: 사용자별 맞춤 대시보드
5. **데이터 시각화 고도화**: 더 다양한 차트 및 그래프

---

**분석 완료**: 이 프로젝트는 캐릭터 챗봇 커뮤니티의 트렌드를 자동으로 모니터링하고 분석하는 잘 구조화된 풀스택 애플리케이션입니다. 백엔드에서 크롤링과 분석을 수행하고, 프론트엔드에서 데이터를 시각적으로 표현하여 사용자에게 제공합니다.
