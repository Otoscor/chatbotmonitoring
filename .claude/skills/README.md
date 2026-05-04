# Claude Code Skills for Monitoring Project

캐릭터 챗봇 모니터링 시스템을 위한 Claude Code 스킬 모음입니다.

---

## 사용 가능한 스킬

| 스킬 | 설명 | 파일 |
|------|------|------|
| `/crawl` | 웹 크롤러 실행 | [crawl.md](./crawl.md) |
| `/export` | 데이터 JSON 내보내기 | [export.md](./export.md) |
| `/deploy` | GitHub Pages 배포 | [deploy.md](./deploy.md) |
| `/dev` | 개발 서버 실행 | [dev.md](./dev.md) |
| `/update` | 전체 업데이트 사이클 | [update.md](./update.md) |
| `/add-crawler` | 새 크롤러 추가 | [add-crawler.md](./add-crawler.md) |
| `/add-page` | 새 프론트엔드 페이지 추가 | [add-page.md](./add-page.md) |
| `/analyze` | 데이터 분석 실행 | [analyze.md](./analyze.md) |
| `/commit` | Git 커밋 생성 | [commit.md](./commit.md) |
| `/test` | 테스트 실행 | [test.md](./test.md) |
| `/refactor` | 코드 리팩토링 가이드 | [refactor.md](./refactor.md) |

---

## 스킬 카테고리

### 데이터 수집 & 처리
- `/crawl` - 각 커뮤니티/서비스에서 데이터 수집
- `/analyze` - 수집된 데이터 분석 (캐릭터 랭킹, 키워드 추출)
- `/export` - JSON 형식으로 내보내기

### 개발
- `/dev` - 로컬 개발 서버 실행
- `/add-crawler` - 새로운 데이터 소스 크롤러 추가
- `/add-page` - 새로운 프론트엔드 페이지 추가
- `/test` - 테스트 실행

### 배포 & 버전 관리
- `/commit` - 커밋 메시지 컨벤션에 맞게 커밋
- `/deploy` - GitHub Pages에 배포
- `/update` - 전체 업데이트 파이프라인 실행

---

## 워크플로우

### 일일 데이터 업데이트
```
/update
```
또는 단계별로:
```
/crawl → /analyze → /export → /deploy
```

### 새로운 데이터 소스 추가
```
/add-crawler charstar https://charstar.ai
```

### 새로운 페이지 개발
```
/add-page Statistics /statistics
/dev --frontend
```

---

## 디자인 시스템

UI 개발 시 [`skills.md`](../skills.md) 파일의 디자인 시스템을 참고하세요:
- 색상 (Light/Dark 모드)
- 타이포그래피
- 간격 및 테두리
- 컴포넌트 스타일
- 애니메이션

---

## 프로젝트 구조

```
monitoring/
├── .claude/
│   ├── skills/         # 스킬 파일들 (이 디렉토리)
│   │   ├── crawl.md
│   │   ├── export.md
│   │   ├── deploy.md
│   │   ├── dev.md
│   │   ├── update.md
│   │   ├── add-crawler.md
│   │   ├── add-page.md
│   │   ├── analyze.md
│   │   ├── commit.md
│   │   ├── test.md
│   │   └── README.md   # 이 파일
│   └── skills.md       # 디자인 시스템
├── frontend/           # React + TypeScript
├── backend/            # Python + FastAPI
└── .github/workflows/  # CI/CD
```

---

## 참고

- vive-md 기반: https://github.com/johunsang/vive-md
- Claude Code 공식 문서: https://docs.anthropic.com/claude-code
