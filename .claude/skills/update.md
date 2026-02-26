# /update - 전체 업데이트 사이클

크롤링 → 분석 → 내보내기 → 배포까지 전체 사이클을 실행합니다.

---

## 사용법

```
/update [옵션]
```

### 옵션
- (기본): 전체 업데이트 사이클
- `--skip-crawl`: 크롤링 건너뛰기
- `--skip-deploy`: 배포 건너뛰기
- `--dry-run`: 실행 없이 계획만 출력

---

## 업데이트 파이프라인

```
┌─────────────────┐
│  1. 크롤링      │  ← 모든 소스에서 데이터 수집
│     /crawl      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 분석        │  ← 캐릭터 랭킹, 키워드 추출
│     /analyze    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. 내보내기    │  ← JSON 파일 생성
│     /export     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. 배포        │  ← GitHub Pages 배포
│     /deploy     │
└─────────────────┘
```

---

## 원클릭 실행

```bash
cd /Users/anipen/Desktop/monitoring
./update_site.sh
```

### update_site.sh 내용
```bash
#!/bin/bash
set -e

echo "=== 데이터 업데이트 시작 ==="

# 1. 크롤링
cd backend
source venv/bin/activate
python -m crawler.run_all

# 2. 분석 & 내보내기
python export_data.py

# 3. Git 커밋 & 푸시
cd ..
git add frontend/public/data/
git commit -m "chore: update data $(date +%Y-%m-%d)"
git push origin main

echo "=== 업데이트 완료 ==="
```

---

## 스케줄 실행

### cron 설정 (매일 오전 9시)
```bash
crontab -e
# 추가:
0 9 * * * cd /Users/anipen/Desktop/monitoring && ./update_site.sh >> logs/update.log 2>&1
```

### launchd 설정 (macOS)
```xml
<!-- ~/Library/LaunchAgents/com.monitoring.update.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.monitoring.update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/anipen/Desktop/monitoring/update_site.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

---

## 실행 로그

업데이트 로그 확인:
```bash
cat logs/update.log
tail -f logs/update.log  # 실시간 모니터링
```

---

## 문제 해결

### 크롤링 실패
- 네트워크 연결 확인
- 각 사이트 접근 가능 여부 확인
- 개별 크롤러 테스트: `/crawl dcinside`

### 배포 실패
- GitHub 인증 확인
- Actions 탭에서 에러 로그 확인
- 수동 배포 시도: `/deploy`
