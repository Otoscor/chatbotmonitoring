# /analyze - 데이터 분석 실행

수집된 데이터에 대해 분석을 수행합니다.

---

## 사용법

```
/analyze [분석유형]
```

### 분석 유형
- (기본): 전체 분석
- `characters` - 캐릭터 언급 분석 및 랭킹
- `keywords` - 키워드 추출 및 트렌드
- `sentiment` - 감성 분석
- `report` - 일일 리포트 생성

---

## 분석 모듈

### 캐릭터 랭킹 (`character_ranker.py`)
- 게시글에서 캐릭터명 추출
- 언급 빈도 기반 랭킹 생성
- 일간/주간/월간 트렌드 계산

```bash
cd /Users/anipen/Desktop/monitoring/backend
source venv/bin/activate
python -m analyzer.character_ranker
```

### 키워드 추출 (`keyword_extractor.py`)
- TF-IDF 기반 키워드 추출
- 불용어 필터링
- 키워드 클러스터링

```bash
python -m analyzer.keyword_extractor
```

### 트렌드 분석 (`trend_analyzer.py`)
- 시계열 데이터 분석
- 급상승/급하락 감지
- 주기성 패턴 분석

```bash
python -m analyzer.trend_analyzer
```

---

## 분석 파이프라인

```
┌─────────────────┐
│   Raw Posts     │  ← SQLite DB
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text Cleaning  │  ← 전처리
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│캐릭터 │ │키워드 │
│추출   │ │추출   │
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│랭킹   │ │트렌드 │
│계산   │ │분석   │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│  Daily Report   │  ← 종합 리포트
└─────────────────┘
```

---

## 분석 결과물

### CharacterMention 테이블
```python
class CharacterMention:
    id: int
    character_name: str
    post_id: int
    mention_count: int
    date: datetime
```

### PostKeyword 테이블
```python
class PostKeyword:
    id: int
    post_id: int
    keyword: str
    score: float  # TF-IDF 점수
```

### DailyReport 테이블
```python
class DailyReport:
    id: int
    date: date
    total_posts: int
    top_characters: JSON
    top_keywords: JSON
    summary: str
```

---

## 분석 설정

`backend/config.py`:
```python
ANALYSIS_CONFIG = {
    "min_mention_count": 3,       # 최소 언급 횟수
    "top_keywords_count": 50,     # 추출할 키워드 수
    "stopwords_file": "data/stopwords.txt",
    "character_dict": "data/characters.json",
}
```

---

## 문제 해결

### 메모리 부족
- 배치 처리 크기 줄이기
- 데이터 기간 제한

### 분석 결과 이상
- 불용어 목록 업데이트
- 캐릭터 사전 확인
- 데이터 품질 검증
