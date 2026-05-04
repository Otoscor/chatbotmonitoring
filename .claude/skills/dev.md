# /dev - 개발 서버 실행

프론트엔드와 백엔드 개발 서버를 실행합니다.

---

## 사용법

```
/dev [옵션]
```

### 옵션
- (기본): 프론트엔드 + 백엔드 동시 실행
- `--frontend`: 프론트엔드만 실행
- `--backend`: 백엔드만 실행

---

## 개발 환경 구성

### 프론트엔드 (React + Vite)
- **포트**: 5173
- **URL**: http://localhost:5173

### 백엔드 (FastAPI)
- **포트**: 8000
- **URL**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

---

## 실행 방법

### 동시 실행 (권장)
```bash
cd /Users/anipen/Desktop/monitoring
npm start
```

### 프론트엔드만
```bash
cd /Users/anipen/Desktop/monitoring/frontend
npm run dev
```

### 백엔드만
```bash
cd /Users/anipen/Desktop/monitoring/backend
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

---

## 프로젝트 구조

```
monitoring/
├── frontend/           # React 프론트엔드
│   ├── src/
│   │   ├── pages/     # 페이지 컴포넌트
│   │   ├── components/ # 재사용 컴포넌트
│   │   └── utils/     # 유틸리티 함수
│   └── public/data/   # 정적 JSON 데이터
│
└── backend/           # Python 백엔드
    ├── api/          # FastAPI 서버
    ├── crawler/      # 웹 크롤러
    ├── analyzer/     # 데이터 분석
    └── models/       # 데이터베이스 모델
```

---

## 환경 설정

### 프론트엔드 의존성 설치
```bash
cd frontend
npm install
```

### 백엔드 의존성 설치
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Playwright 설치 (크롤러용)
```bash
playwright install chromium
```

---

## 개발 모드 vs 프로덕션 모드

| 항목 | 개발 모드 | 프로덕션 모드 |
|------|-----------|---------------|
| 데이터 소스 | 로컬 API 서버 | 정적 JSON 파일 |
| Hot Reload | O | X |
| 소스맵 | O | X |
| 빌드 최적화 | X | O |

---

## 문제 해결

### 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :5173
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### 환경변수 설정
- 프론트엔드: `frontend/.env.local`
- 백엔드: `backend/.env`
