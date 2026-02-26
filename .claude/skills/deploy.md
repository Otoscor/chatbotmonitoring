# /deploy - GitHub Pages 배포

프론트엔드를 빌드하고 GitHub Pages에 배포합니다.

---

## 사용법

```
/deploy [옵션]
```

### 옵션
- `--build-only`: 빌드만 수행 (배포 안 함)
- `--skip-build`: 빌드 건너뛰고 배포만

---

## 배포 아키텍처

```
Local Development
      │
      ▼
┌─────────────────┐
│  npm run build  │  ← Vite 빌드
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   git commit    │  ← 변경사항 커밋
│   git push      │  ← GitHub에 푸시
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │  ← 자동 빌드 & 배포
│  deploy.yml     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub Pages   │  ← 정적 호스팅
└─────────────────┘
```

---

## 실행 순서

1. **프론트엔드 빌드**
   ```bash
   cd /Users/anipen/Desktop/monitoring/frontend
   npm run build
   ```

2. **빌드 결과 확인**
   - 출력 디렉토리: `frontend/dist/`
   - 빌드 에러 없는지 확인

3. **변경사항 커밋 & 푸시**
   ```bash
   git add .
   git commit -m "chore: update data and build"
   git push origin main
   ```

4. **GitHub Actions 확인**
   - `.github/workflows/deploy.yml` 워크플로우 실행됨
   - Actions 탭에서 배포 상태 확인

5. **배포 완료 확인**
   - URL: `https://otoscor.github.io/chatbotmonitoring/`

---

## 관련 파일

| 파일 | 설명 |
|------|------|
| `.github/workflows/deploy.yml` | GitHub Actions 워크플로우 |
| `frontend/vite.config.ts` | Vite 빌드 설정 |
| `frontend/package.json` | 빌드 스크립트 |

---

## 배포 체크리스트

- [ ] 크롤링 완료
- [ ] JSON 내보내기 완료
- [ ] 프론트엔드 빌드 성공
- [ ] 타입 에러 없음
- [ ] 로컬에서 프리뷰 확인 (`npm run preview`)
- [ ] Git 커밋 & 푸시
- [ ] GitHub Actions 성공

---

## 문제 해결

### 빌드 실패
- `npm install` 재실행
- TypeScript 타입 에러 확인
- 의존성 버전 충돌 확인

### 배포 후 404 에러
- `vite.config.ts`의 `base` 설정 확인
- GitHub Pages 설정에서 브랜치 확인

### 이미지/에셋 로드 실패
- 경로가 `/chatbotmonitoring/` 기준인지 확인
- public 폴더 내 파일 확인
