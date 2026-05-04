# 캐릭터 챗봇 모니터링 시스템

캐릭터 챗봇 커뮤니티의 동향을 모니터링하고 분석하는 시스템입니다.

## 🌐 배포된 사이트

**GitHub Pages**: https://otoscor.github.io/chatbotmonitoring/

## 📋 주요 기능

- 📊 **대시보드**: 전체 통계 및 트렌드 시각화
- 🔥 **키워드 분석**: 인기 키워드 및 트렌드 추적
- 👥 **캐릭터 랭킹**: 언급 빈도 기반 캐릭터 순위
- 🤖 **챗봇 서비스 모니터링**: Zeta, Babechat, Lunatalk 인기 캐릭터 순위
- 📈 **일일 리포트**: 자동 생성되는 일일 분석 보고서

## 🏗️ 아키텍처

이 프로젝트는 **정적 사이트 배포** 방식을 사용합니다:

```
로컬 (관리자) → 크롤링 → SQLite DB → JSON Export
                                          ↓
                        GitHub Repository (commit & push)
                                          ↓
                        GitHub Actions (자동 빌드)
                                          ↓
                         GitHub Pages (정적 사이트)
                                          ↓
                           사용자 (데이터 조회)
```

### 장점
- ✅ 완전 무료 (GitHub Pages)
- ✅ 빠른 로딩 (CDN)
- ✅ 서버 관리 불필요
- ✅ 자동 배포

## 🚀 시작하기

### 1. 저장소 클론

```bash
git clone https://github.com/Otoscor/chatbotmonitoring.git
cd chatbotmonitoring
```

### 2. 백엔드 설정 (로컬 전용)

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 크롤링 실행 (선택사항)
python -m crawler.multi_crawler

# 리포트 생성 (선택사항)
python -m scheduler.jobs
```

### 3. 프론트엔드 설정 (로컬 개발)

```bash
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```

로컬 개발 시 `http://localhost:3000`에서 확인

## 📦 데이터 업데이트 및 배포

### 원클릭 업데이트 (추천)

```bash
# 프로젝트 루트에서 실행
./update_site.sh
```

이 스크립트는:
1. 데이터를 JSON으로 export
2. Git 커밋 및 푸시
3. GitHub Actions가 자동으로 배포

### 수동 업데이트

```bash
# 1. 데이터 Export
cd backend
python export_data.py

# 2. Git 커밋 및 푸시
cd ..
git add frontend/public/data/
git commit -m "chore: 데이터 업데이트"
git push origin main

# 3. GitHub Actions가 자동으로 배포합니다
```

## 🗂️ 프로젝트 구조

```
monitoring/
├── backend/                    # 백엔드 (로컬 전용)
│   ├── api/                   # FastAPI 서버 (개발용)
│   ├── crawler/               # 크롤링 모듈
│   ├── analyzer/              # 데이터 분석 모듈
│   ├── models/                # 데이터베이스 모델
│   ├── export_data.py         # JSON Export 스크립트
│   └── requirements.txt       # Python 패키지
├── frontend/                   # 프론트엔드
│   ├── public/
│   │   └── data/              # JSON 데이터 파일
│   ├── src/
│   │   ├── components/        # React 컴포넌트
│   │   ├── pages/             # 페이지
│   │   ├── hooks/             # 커스텀 훅
│   │   └── utils/             # 유틸리티
│   └── package.json
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions 배포 설정
└── update_site.sh             # 원클릭 업데이트 스크립트
```

## 🛠️ 기술 스택

### 백엔드
- Python 3.11+
- FastAPI (개발 서버)
- SQLAlchemy (ORM)
- SQLite (데이터베이스)
- BeautifulSoup4, Playwright (크롤링)
- scikit-learn (데이터 분석)

### 프론트엔드
- React + TypeScript
- Vite
- TailwindCSS
- Recharts (차트)
- Axios

### 배포
- GitHub Pages
- GitHub Actions

## 📊 데이터 소스

- 디시인사이드 (뤼튼 마이너갤, AI챗팅 마이너갤)
- 아카라이브 (캐릭터AI)
- Zeta (제타)
- Babechat (베이브챗)
- Lunatalk (루나톡)

## 🔧 환경 변수

### 프론트엔드 (.env)

```bash
# 로컬 개발용 API URL
VITE_API_URL=http://localhost:8001/api

# 정적 데이터 모드 (배포용)
VITE_USE_STATIC_DATA=false
```

## 📝 라이선스

MIT License

## 👤 작성자

Otoscor

## 🤝 기여

이슈와 PR을 환영합니다!
