# 캐릭터 챗봇 커뮤니티 모니터링 시스템

캐릭터 챗봇 관련 커뮤니티(디시인사이드 등)의 동향과 인기 캐릭터를 모니터링하고 분석하는 시스템입니다.

## 주요 기능

- **자동 크롤링**: 매일 자정에 자동으로 커뮤니티 게시글 수집
- **키워드 분석**: 한국어 NLP를 활용한 키워드 추출 및 트렌드 분석
- **캐릭터 랭킹**: 언급 빈도 기반 인기 캐릭터 순위 산출
- **일일 리포트**: 매일 자동 생성되는 커뮤니티 동향 리포트
- **웹 대시보드**: 실시간 데이터 시각화 및 분석 결과 제공

## 기술 스택

### 백엔드
- Python 3.10+
- FastAPI (REST API)
- SQLAlchemy + SQLite (데이터베이스)
- BeautifulSoup4 + httpx (크롤링)
- KiwiPiPy (한국어 NLP)
- APScheduler (작업 스케줄링)

### 프론트엔드
- React 18 + TypeScript
- Vite (빌드 도구)
- TailwindCSS (스타일링)
- Recharts (데이터 시각화)
- React Router (라우팅)

## 프로젝트 구조

```
monitoring/
├── backend/
│   ├── api/              # FastAPI 라우터 및 엔드포인트
│   ├── analyzer/         # 분석 엔진 (키워드, 트렌드, 캐릭터)
│   ├── crawler/          # 웹 크롤러
│   ├── models/           # 데이터베이스 모델
│   ├── scheduler/        # 스케줄링 작업
│   ├── config.py         # 설정 관리
│   └── requirements.txt  # Python 의존성
├── frontend/
│   ├── src/
│   │   ├── components/   # UI 컴포넌트
│   │   ├── pages/        # 페이지 컴포넌트
│   │   ├── hooks/        # 커스텀 React 훅
│   │   └── utils/        # 유틸리티 함수
│   └── package.json      # Node.js 의존성
└── README.md
```

## 설치 및 실행

### 1. 백엔드 설정

```bash
cd backend

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# KiwiPiPy 설치 (한국어 NLP)
pip install kiwipiepy

# 환경변수 설정 (선택사항)
cp .env.example .env
# .env 파일에서 설정 수정

# API 서버 실행
cd api
python main.py
```

API 서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

### 2. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드는 기본적으로 `http://localhost:3000`에서 실행됩니다.

### 3. 스케줄러 실행 (선택사항)

자동 크롤링을 원하는 경우:

```bash
cd backend/scheduler
python jobs.py
```

## API 엔드포인트

### 게시글
- `GET /api/posts` - 게시글 목록 조회
- `GET /api/posts/{post_id}` - 특정 게시글 조회
- `GET /api/posts/stats/daily` - 일일 통계

### 리포트
- `GET /api/reports` - 리포트 목록
- `GET /api/reports/latest` - 최신 리포트
- `GET /api/reports/{date}` - 특정 날짜 리포트
- `POST /api/reports/generate` - 수동 리포트 생성

### 분석
- `GET /api/keywords/trending` - 트렌딩 키워드
- `GET /api/characters/ranking` - 캐릭터 랭킹

### 크롤링
- `POST /api/crawl` - 수동 크롤링 실행

## 설정

`backend/config.py` 또는 `.env` 파일에서 다음 설정을 변경할 수 있습니다:

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./monitoring.db` | 데이터베이스 연결 URL |
| `CRAWL_DELAY_SECONDS` | `1.5` | 크롤링 요청 간 대기 시간 |
| `MAX_PAGES_PER_CRAWL` | `10` | 한 번에 크롤링할 최대 페이지 수 |
| `TARGET_GALLERY_ID` | `charai` | 크롤링 대상 갤러리 ID |

## 법적 고려사항

이 시스템은 공개된 게시글만 수집하며, 다음 원칙을 준수합니다:

1. **robots.txt 준수**: 크롤링 정책 확인 및 준수
2. **Rate Limiting**: 서버 부하 최소화를 위한 요청 속도 제한
3. **분석 목적**: 수집 데이터는 통계 분석 목적으로만 사용
4. **개인정보 보호**: 개인정보 수집 및 재배포 금지

## 확장 가능성

- 추가 커뮤니티 크롤러 (아카라이브, 에펨코리아 등)
- 이메일/슬랙 알림 기능
- 감성 분석 고도화
- 사용자 인증 시스템

## 라이센스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.
