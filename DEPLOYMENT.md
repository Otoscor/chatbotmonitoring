# 배포 가이드

## 📋 목차
1. [백엔드 배포 (Render)](#백엔드-배포-render)
2. [프론트엔드 배포 (Vercel)](#프론트엔드-배포-vercel)
3. [환경 변수 설정](#환경-변수-설정)
4. [배포 후 확인사항](#배포-후-확인사항)

---

## 🚀 백엔드 배포 (Render)

### 1단계: PostgreSQL 데이터베이스 생성

1. **Render 대시보드 접속**
   - https://dashboard.render.com 로그인

2. **New PostgreSQL 생성**
   - 상단의 `New +` 버튼 클릭
   - `PostgreSQL` 선택

3. **데이터베이스 설정**
   ```
   Name: chatbot-monitoring-db
   Database: monitoring (또는 원하는 이름)
   User: monitoring (자동 생성됨)
   Region: Singapore (또는 가까운 지역)
   Plan: Free
   ```

4. **생성 완료**
   - `Create Database` 클릭
   - **Internal Database URL** 복사해두기 (나중에 사용)
   - 형식: `postgresql://user:password@host:5432/database`

---

### 2단계: 백엔드 웹 서비스 생성

1. **New Web Service 생성**
   - `New +` 버튼 클릭
   - `Web Service` 선택

2. **GitHub 저장소 연결**
   - `Connect a repository` 선택
   - GitHub 계정 연동 (처음이면 승인 필요)
   - `Otoscor/chatbotmonitoring` 저장소 선택
   - `Connect` 클릭

3. **배포 설정**
   ```
   Name: chatbot-monitoring-api
   Region: Singapore (또는 프론트엔드와 동일한 지역)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: cd api && uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

4. **환경 변수 설정** (중요!)
   - `Advanced` 섹션 확장
   - `Add Environment Variable` 클릭
   - 다음 변수들 추가:

   ```
   DATABASE_URL = [1단계에서 복사한 Internal Database URL]
   API_HOST = 0.0.0.0
   API_PORT = 10000
   ```

5. **배포 시작**
   - `Create Web Service` 클릭
   - 첫 배포는 5~10분 소요
   - 로그를 확인하여 에러가 없는지 확인

6. **배포 URL 확인**
   - 배포 완료 후 URL 확인 (예: `https://chatbot-monitoring-api.onrender.com`)
   - 이 URL을 복사해두기 (프론트엔드에서 사용)

7. **헬스 체크**
   - 브라우저에서 `https://your-app.onrender.com/health` 접속
   - `{"status": "healthy"}` 응답 확인

---

## 🌐 프론트엔드 배포 (Vercel)

### 1단계: Vercel 프로젝트 생성

1. **Vercel 접속**
   - https://vercel.com 로그인
   - GitHub 계정으로 로그인

2. **새 프로젝트 추가**
   - `Add New...` → `Project` 클릭
   - `Import Git Repository` 선택
   - `Otoscor/chatbotmonitoring` 저장소 선택
   - `Import` 클릭

3. **프로젝트 설정**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build (자동 설정)
   Output Directory: dist (자동 설정)
   Install Command: npm install (자동 설정)
   ```

4. **환경 변수 설정** (중요!)
   - `Environment Variables` 섹션에서:
   ```
   Name: VITE_API_URL
   Value: https://chatbot-monitoring-api.onrender.com/api
   ```
   (위의 URL은 Render에서 배포한 백엔드 URL + `/api`)

5. **배포 시작**
   - `Deploy` 클릭
   - 배포 완료 (보통 1~2분 소요)

6. **배포 URL 확인**
   - 배포 완료 후 자동으로 생성된 URL 확인
   - 예: `https://chatbotmonitoring-xxx.vercel.app`

---

## 🔑 환경 변수 설정

### 백엔드 (Render)
```bash
DATABASE_URL=postgresql://user:password@host:5432/database
API_HOST=0.0.0.0
API_PORT=10000
```

### 프론트엔드 (Vercel)
```bash
VITE_API_URL=https://your-backend.onrender.com/api
```

---

## ✅ 배포 후 확인사항

### 1. 백엔드 확인
- [ ] 헬스 체크: `https://your-backend.onrender.com/health`
- [ ] API 문서: `https://your-backend.onrender.com/docs`
- [ ] 데이터베이스 연결 확인
- [ ] CORS 설정 확인 (프론트엔드에서 API 호출 가능한지)

### 2. 프론트엔드 확인
- [ ] 웹사이트 접속 확인
- [ ] API 연동 확인 (데이터 로딩)
- [ ] 모든 페이지 동작 확인
- [ ] 크롤링 기능 테스트

### 3. Render 슬립 모드 방지 (선택사항)
Render 무료 플랜은 15분 미사용 시 슬립 모드로 전환됩니다.
이를 방지하려면:

**방법 1: UptimeRobot (추천)**
- https://uptimerobot.com 가입
- 5분마다 헬스 체크 엔드포인트 호출하도록 설정

**방법 2: cron-job.org**
- https://cron-job.org 가입
- 5분마다 `https://your-backend.onrender.com/health` 호출

---

## 🔄 자동 배포 설정

### GitHub 푸시 시 자동 배포
- Render와 Vercel 모두 `main` 브랜치에 푸시하면 자동으로 배포됩니다
- 별도 설정 불필요

### 배포 확인
```bash
# 로컬에서 변경사항 푸시
git add .
git commit -m "변경사항 메시지"
git push origin main

# Render와 Vercel 대시보드에서 배포 진행 상황 확인
```

---

## 🐛 트러블슈팅

### 백엔드 배포 실패
1. **Build 실패**
   - Render 로그 확인
   - `requirements.txt` 패키지 버전 확인
   - Python 버전 확인 (Python 3.11 권장)

2. **Start 실패**
   - Start Command 확인: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - 환경 변수 `DATABASE_URL` 설정 확인

3. **데이터베이스 연결 실패**
   - `DATABASE_URL` 형식 확인
   - PostgreSQL 데이터베이스가 실행 중인지 확인

### 프론트엔드 배포 실패
1. **Build 실패**
   - Vercel 로그 확인
   - Root Directory가 `frontend`로 설정되었는지 확인

2. **API 연결 실패**
   - `VITE_API_URL` 환경 변수 확인
   - 백엔드 URL 끝에 `/api` 추가 확인
   - CORS 설정 확인

---

## 📚 추가 자료

- [Render 공식 문서](https://render.com/docs)
- [Vercel 공식 문서](https://vercel.com/docs)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
