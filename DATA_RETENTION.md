# 데이터 유효기간 관리

캐릭터 챗봇 모니터링 시스템은 데이터의 유효기간을 관리하여 오래된 데이터가 계속 표시되지 않도록 합니다.

## 자동 필터링

### API 기본 유효기간

각 API 엔드포인트는 기본적으로 최근 데이터만 반환합니다:

- **게시글 목록** (`/api/posts`): 최근 **30일** 이내 데이터 (기본값)
- **인기 게시글** (`/api/posts/popular`): 최근 **7일** 이내 데이터 (기본값)

파라미터를 통해 유효기간을 조정할 수 있습니다:

```bash
# 최근 60일 이내 게시글 조회
GET /api/posts?days=60

# 최근 14일 이내 인기 게시글 조회
GET /api/posts/popular?days=14
```

## 수동 데이터 정리

`cleanup_old_data.py` 스크립트를 사용하여 오래된 데이터를 삭제할 수 있습니다.

### 기본 보관 기간

- **게시글**: 90일
- **리포트**: 180일
- **캐릭터 서비스**: 30일
- **뉴스 기사**: 60일
- **앱 리뷰**: 90일

### 사용법

#### 1. Dry Run (삭제 전 확인)

실제 삭제 없이 어떤 데이터가 삭제 대상인지 확인:

```bash
cd backend
python3 cleanup_old_data.py --dry-run
```

#### 2. 실제 삭제

```bash
python3 cleanup_old_data.py
```

#### 3. 보관 기간 커스터마이징

```bash
# 게시글 60일, 리포트 90일 이전 데이터 삭제
python3 cleanup_old_data.py --posts-days 60 --reports-days 90

# 캐릭터 서비스 데이터만 7일 이전 삭제
python3 cleanup_old_data.py --characters-days 7
```

### 모든 옵션

```bash
python3 cleanup_old_data.py --help
```

```
옵션:
  --posts-days N          게시글 보관 기간 (기본: 90일)
  --reports-days N        리포트 보관 기간 (기본: 180일)
  --characters-days N     캐릭터 서비스 보관 기간 (기본: 30일)
  --news-days N          뉴스 보관 기간 (기본: 60일)
  --reviews-days N       앱 리뷰 보관 기간 (기본: 90일)
  --dry-run              실제 삭제 없이 조회만 수행
```

## 정기 자동 실행 (권장)

### Cron 설정 (Linux/Mac)

매주 일요일 새벽 3시에 자동 정리:

```bash
crontab -e
```

다음 라인 추가:

```
0 3 * * 0 cd /path/to/monitoring/backend && /usr/bin/python3 cleanup_old_data.py >> /var/log/cleanup.log 2>&1
```

### Render.com 스케줄러

Render.com에서 Cron Job을 추가:

1. Dashboard → "New" → "Cron Job"
2. 다음 설정:
   - **Command**: `python3 backend/cleanup_old_data.py`
   - **Schedule**: `0 3 * * 0` (매주 일요일 3시)

## 주의사항

⚠️ **삭제된 데이터는 복구할 수 없습니다!**

- 처음 실행 시 `--dry-run` 옵션으로 확인하세요
- 중요한 데이터는 백업 후 삭제하세요
- 보관 기간을 너무 짧게 설정하지 마세요

## 데이터베이스 백업

정리 전 데이터베이스 백업:

```bash
# SQLite 백업
cp backend/monitoring.db backend/monitoring.db.backup.$(date +%Y%m%d)
```
