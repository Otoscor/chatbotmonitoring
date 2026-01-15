"""
키워드 추출 모듈
- 한국어 형태소 분석
- TF-IDF 기반 키워드 추출
"""
import re
from typing import List, Dict, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# KiwiPiPy 지연 로딩
_kiwi = None


def get_kiwi():
    """Kiwi 인스턴스 지연 로딩"""
    global _kiwi
    if _kiwi is None:
        try:
            from kiwipiepy import Kiwi
            _kiwi = Kiwi()
            logger.info("Kiwi 형태소 분석기 로드 완료")
        except ImportError:
            logger.warning("kiwipiepy가 설치되지 않았습니다. 간단한 토큰화를 사용합니다.")
            _kiwi = None
    return _kiwi


# 불용어 리스트 (분석에서 제외할 단어들)
STOPWORDS = {
    # 일반 불용어
    "있다", "하다", "되다", "이다", "것", "수", "등", "더", "좀", "그", "저",
    "이", "그것", "저것", "뭐", "무엇", "어떤", "이런", "저런", "그런",
    "하는", "하면", "해서", "하고", "하지", "않다", "없다", "같다",
    # 디시인사이드 특화 불용어
    "갤러리", "글", "댓글", "추천", "비추", "게시글", "작성",
    "ㅋㅋ", "ㅋㅋㅋ", "ㅋㅋㅋㅋ", "ㅎㅎ", "ㅎㅎㅎ", "ㄷㄷ", "ㅇㅇ",
    "ㄹㅇ", "ㅈㄱㄴ", "ㅁㅊ", "ㅂㅅ", "ㄱㅇㄷ",
    # AI/캐릭터 챗봇 관련 일반 단어 (너무 일반적인 것들)
    "캐릭터", "챗봇", "봇", "채팅", "대화",
}


def tokenize_simple(text: str) -> List[str]:
    """간단한 토큰화 (형태소 분석기 없이)"""
    # 한글, 영문, 숫자만 추출
    tokens = re.findall(r"[가-힣]+|[a-zA-Z]+", text)
    # 2글자 이상만 유지
    tokens = [t for t in tokens if len(t) >= 2]
    return tokens


def tokenize_with_kiwi(text: str) -> List[str]:
    """Kiwi를 이용한 형태소 분석"""
    kiwi = get_kiwi()
    if kiwi is None:
        return tokenize_simple(text)
    
    tokens = []
    result = kiwi.tokenize(text)
    
    # 명사(NNG, NNP), 동사(VV), 형용사(VA), 외래어(SL) 추출
    target_tags = {"NNG", "NNP", "VV", "VA", "SL"}
    
    for token in result:
        if token.tag in target_tags:
            # 2글자 이상만 유지
            if len(token.form) >= 2:
                tokens.append(token.form)
    
    return tokens


def extract_keywords(texts: List[str], top_n: int = 50) -> List[Dict[str, any]]:
    """
    텍스트 목록에서 키워드 추출
    
    Args:
        texts: 분석할 텍스트 목록
        top_n: 반환할 상위 키워드 수
        
    Returns:
        [{"keyword": "xxx", "count": 10, "score": 0.5}, ...]
    """
    all_tokens = []
    
    for text in texts:
        tokens = tokenize_with_kiwi(text)
        # 불용어 제거
        tokens = [t for t in tokens if t.lower() not in STOPWORDS and t not in STOPWORDS]
        all_tokens.extend(tokens)
    
    # 빈도 계산
    counter = Counter(all_tokens)
    total_count = len(all_tokens)
    
    keywords = []
    for keyword, count in counter.most_common(top_n):
        score = count / total_count if total_count > 0 else 0
        keywords.append({
            "keyword": keyword,
            "count": count,
            "score": round(score, 4)
        })
    
    return keywords


def extract_keywords_tfidf(texts: List[str], top_n: int = 50) -> List[Dict[str, any]]:
    """
    TF-IDF 기반 키워드 추출
    
    Args:
        texts: 분석할 텍스트 목록
        top_n: 반환할 상위 키워드 수
        
    Returns:
        [{"keyword": "xxx", "count": 10, "score": 0.5}, ...]
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        logger.warning("scikit-learn이 설치되지 않았습니다. 빈도 기반 추출을 사용합니다.")
        return extract_keywords(texts, top_n)
    
    # 각 텍스트를 토큰화하여 공백으로 연결
    processed_texts = []
    for text in texts:
        tokens = tokenize_with_kiwi(text)
        tokens = [t for t in tokens if t.lower() not in STOPWORDS and t not in STOPWORDS]
        processed_texts.append(" ".join(tokens))
    
    if not processed_texts or all(not t.strip() for t in processed_texts):
        return []
    
    # TF-IDF 계산
    vectorizer = TfidfVectorizer(max_features=top_n * 2)
    try:
        tfidf_matrix = vectorizer.fit_transform(processed_texts)
    except ValueError:
        return extract_keywords(texts, top_n)
    
    # 전체 문서에서의 평균 TF-IDF 점수
    feature_names = vectorizer.get_feature_names_out()
    avg_scores = tfidf_matrix.mean(axis=0).A1
    
    # 빈도도 함께 계산
    all_tokens = []
    for text in processed_texts:
        all_tokens.extend(text.split())
    counter = Counter(all_tokens)
    
    keywords = []
    for idx, score in enumerate(avg_scores):
        keyword = feature_names[idx]
        count = counter.get(keyword, 0)
        keywords.append({
            "keyword": keyword,
            "count": count,
            "score": round(float(score), 4)
        })
    
    # 점수 기준 정렬
    keywords.sort(key=lambda x: x["score"], reverse=True)
    
    return keywords[:top_n]


def extract_ngrams(texts: List[str], n: int = 2, top_n: int = 20) -> List[Dict[str, any]]:
    """
    N-gram 추출 (연속된 단어 조합)
    
    Args:
        texts: 분석할 텍스트 목록
        n: n-gram 크기 (기본 2 = bigram)
        top_n: 반환할 상위 개수
        
    Returns:
        [{"ngram": "xxx yyy", "count": 10}, ...]
    """
    all_ngrams = []
    
    for text in texts:
        tokens = tokenize_with_kiwi(text)
        tokens = [t for t in tokens if t.lower() not in STOPWORDS and t not in STOPWORDS]
        
        # n-gram 생성
        for i in range(len(tokens) - n + 1):
            ngram = " ".join(tokens[i:i + n])
            all_ngrams.append(ngram)
    
    counter = Counter(all_ngrams)
    
    return [{"ngram": ngram, "count": count} for ngram, count in counter.most_common(top_n)]
