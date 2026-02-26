# /commit - Git 커밋 생성

프로젝트 컨벤션에 맞는 Git 커밋을 생성합니다.

---

## 사용법

```
/commit [메시지]
```

### 예시
```
/commit 새로운 크롤러 추가
```

---

## 커밋 메시지 컨벤션

### 형식
```
<type>: <subject>

<body>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### 타입 (Type)
| 타입 | 설명 |
|------|------|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `refactor` | 코드 리팩토링 |
| `style` | 스타일/UI 변경 |
| `docs` | 문서 수정 |
| `chore` | 빌드, 설정 파일 등 기타 변경 |
| `test` | 테스트 추가/수정 |

### 제목 (Subject)
- 한글 또는 영어
- 50자 이내
- 마침표 없이 작성
- 명령형으로 작성 ("추가한다" X, "추가" O)

### 본문 (Body)
- 선택사항
- 변경 이유와 내용 설명
- 72자마다 줄바꿈

---

## 커밋 절차

### 1. 변경사항 확인
```bash
git status
git diff
```

### 2. 스테이징
```bash
# 특정 파일만
git add <파일경로>

# 전체 (주의해서 사용)
git add .
```

### 3. 커밋
```bash
git commit -m "$(cat <<'EOF'
feat: 새로운 기능 설명

상세한 변경 내용

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## 최근 커밋 히스토리

프로젝트의 기존 커밋 스타일 참고:
```
8e55903 refactor: 모든 아이콘을 픽셀아트 스타일로 통일
b69a1fa fix: 비밀번호 에러 체크 로직 개선
2d5d103 fix: 비밀번호 입력 폼 외부 클릭 감지 개선
66dc865 feat: 비밀번호 입력 폼 인터랙션 개선
d0d27e5 style: 캐릭터 샘플 생성 CTA 버튼 스타일 수정
```

---

## 주의사항

### 커밋하지 말 것
- `.env` 파일 (환경변수, API 키)
- `node_modules/` 디렉토리
- `venv/` 가상환경
- `*.sqlite` 데이터베이스 파일
- IDE 설정 파일

### .gitignore 확인
```
.env
.env.local
node_modules/
venv/
*.sqlite
*.db
.DS_Store
```

---

## 유용한 명령어

```bash
# 마지막 커밋 수정 (push 전에만!)
git commit --amend

# 커밋 되돌리기
git revert <commit-hash>

# 로그 확인
git log --oneline -10
```
