# 🎯 크롤링 대상 사이트

캐릭터 챗봇 커뮤니티 모니터링 시스템에서 수집하는 사이트 목록입니다.

## 📋 현재 크롤링 중인 사이트

### 1. 뤼튼 마이너갤러리
- **URL**: https://gall.dcinside.com/mgallery/board/lists/?id=wrtnai
- **타입**: 디시인사이드 마이너갤러리
- **설명**: 뤼튼 AI 챗봇 관련 커뮤니티
- **활동량**: 높음 (페이지당 약 50개 게시글)

### 2. AI챗팅 마이너갤러리
- **URL**: https://gall.dcinside.com/mgallery/board/lists/?id=aichatting
- **타입**: 디시인사이드 마이너갤러리
- **설명**: AI 채팅 관련 종합 커뮤니티
- **활동량**: 높음 (페이지당 약 50개 게시글)

### 3. 아카라이브 캐릭터AI
- **URL**: https://arca.live/b/characterai
- **타입**: 아카라이브 채널
- **설명**: Character.AI 관련 커뮤니티
- **활동량**: 보통 (페이지당 약 40개 게시글)

---

## 🔧 크롤러 설정

### 기본 설정 (`backend/config.py`)

\`\`\`python
target_galleries: List[dict] = [
    {
        "id": "wrtnai",
        "name": "뤼튼 마이너갤",
        "type": "dcinside_minor",
        "url": "https://gall.dcinside.com/mgallery/board/lists/?id=wrtnai"
    },
    {
        "id": "aichatting",
        "name": "AI챗팅 마이너갤",
        "type": "dcinside_minor",
        "url": "https://gall.dcinside.com/mgallery/board/lists/?id=aichatting"
    },
    {
        "id": "characterai",
        "name": "아카라이브 캐릭터AI",
        "type": "arcalive",
        "url": "https://arca.live/b/characterai"
    }
]
\`\`\`

### 크롤링 파라미터
- **딜레이**: 1.5초 (사이트 부하 방지)
- **페이지 수**: 3페이지 (테스트 중)
- **재시도 횟수**: 최대 3회

---

## 📊 크롤링 결과 (테스트)

최근 테스트 결과 (2페이지 기준):
- ✅ 뤼튼 마이너갤: 100개 게시글 수집
- ✅ AI챗팅 마이너갤: 100개 게시글 수집  
- ✅ 아카라이브 캐릭터AI: 81개 게시글 수집

**총합**: 281개 게시글 (약 30초 소요)

---

## 🆕 새로운 사이트 추가 방법

### 1. 디시인사이드 갤러리 추가

\`\`\`python
# backend/config.py
{
    "id": "갤러리ID",  # URL의 ?id= 부분
    "name": "갤러리명",
    "type": "dcinside_minor",  # 또는 "dcinside" (일반갤)
    "url": "https://gall.dcinside.com/mgallery/board/lists/?id=갤러리ID"
}
\`\`\`

### 2. 아카라이브 채널 추가

\`\`\`python
# backend/config.py
{
    "id": "채널ID",  # URL의 /b/ 다음 부분
    "name": "채널명",
    "type": "arcalive",
    "url": "https://arca.live/b/채널ID"
}
\`\`\`

### 3. 적용

설정 파일 수정 후 백엔드 재시작:
\`\`\`bash
cd /Users/anipen/Desktop/monitoring/backend/api
python3 main.py
\`\`\`

---

## ⚠️  크롤링 주의사항

1. **Rate Limiting**: 각 사이트 간 2초 딜레이 적용
2. **로봇 배제 표준**: robots.txt 준수
3. **법적 준수**: 개인정보 수집 없음, 공개 게시글만 수집
4. **서버 부하**: 과도한 크롤링 자제

---

## 🔍 지원되는 크롤러

1. **DCInsideCrawler** (`backend/crawler/dcinside_crawler.py`)
   - 일반 갤러리 지원
   - 마이너 갤러리 지원
   
2. **ArcaliveCrawler** (`backend/crawler/arcalive_crawler.py`)
   - 아카라이브 채널 지원

3. **MultiCrawler** (`backend/crawler/multi_crawler.py`)
   - 모든 사이트 통합 크롤링

---

## 📝 수집 데이터

각 게시글당 다음 정보를 수집합니다:
- 게시글 ID
- 갤러리/채널 ID
- 제목
- 작성자
- 작성일
- 조회수
- 추천수
- 댓글수
- URL

---

**마지막 업데이트**: 2026-01-14
