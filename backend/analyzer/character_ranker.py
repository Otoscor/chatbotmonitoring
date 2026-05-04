"""
캐릭터 랭킹 분석 모듈
- 캐릭터 이름 추출 및 언급 빈도 분석
"""
import re
from typing import List, Dict, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# 인기 캐릭터 챗봇 플랫폼 및 서비스
KNOWN_PLATFORMS = {
    "character.ai", "캐릭터ai", "캐릭터 ai", "c.ai", "시에이아이",
    "chai", "차이", "replika", "레플리카",
    "janitor ai", "제니터", "jailbreak",
    "spicychat", "스파이시챗",
    "crushon", "크러션",
    "talkie", "토키", "botify", "보티파이",
    "poe", "포우", "클로드", "claude", "gpt", "chatgpt",
}

# 일반적으로 캐릭터가 아닌 단어들
NON_CHARACTER_WORDS = {
    "캐릭터", "챗봇", "봇", "ai", "채팅", "대화", "설정", "프롬프트",
    "페르소나", "시나리오", "설명", "소개", "공략", "공유",
    "추천", "질문", "답변", "리뷰", "후기", "버그", "오류",
    "업데이트", "패치", "뉴비", "초보", "고수", "도움",
    "사진", "이미지", "그림", "일러스트", "스크린샷",
}


def extract_character_names(text: str) -> List[str]:
    """
    텍스트에서 캐릭터 이름 후보 추출
    
    패턴:
    - [캐릭터명] 대괄호 안의 텍스트
    - "캐릭터명" 따옴표 안의 텍스트
    - 《캐릭터명》 이중 꺾쇠 안의 텍스트
    - xxx봇 형태
    """
    candidates = []
    
    # 대괄호 패턴: [캐릭터명]
    bracket_matches = re.findall(r"\[([^\]]{2,30})\]", text)
    candidates.extend(bracket_matches)
    
    # 따옴표 패턴: "캐릭터명", '캐릭터명'
    quote_matches = re.findall(r'["\']([^"\']{2,30})["\']', text)
    candidates.extend(quote_matches)
    
    # 이중 꺾쇠 패턴: 《캐릭터명》
    double_angle_matches = re.findall(r"《([^》]{2,30})》", text)
    candidates.extend(double_angle_matches)
    
    # 봇 접미사 패턴
    bot_matches = re.findall(r"([가-힣a-zA-Z0-9]{2,15})(?:봇|bot)", text, re.IGNORECASE)
    candidates.extend(bot_matches)
    
    # 정제 및 필터링
    cleaned = []
    for name in candidates:
        name = name.strip()
        name_lower = name.lower()
        
        # 필터링 조건
        if len(name) < 2 or len(name) > 30:
            continue
        if name_lower in NON_CHARACTER_WORDS:
            continue
        if name_lower in KNOWN_PLATFORMS:
            continue
        if name.isdigit():
            continue
        # URL이나 이메일 패턴 제외
        if re.match(r"https?://|www\.|@", name):
            continue
        
        cleaned.append(name)
    
    return cleaned


def rank_characters(texts: List[str], top_n: int = 20) -> List[Dict[str, any]]:
    """
    텍스트 목록에서 캐릭터 언급 빈도 분석
    
    Args:
        texts: 분석할 텍스트 목록 (게시글 제목 등)
        top_n: 반환할 상위 캐릭터 수
        
    Returns:
        [{"name": "캐릭터명", "mentions": 10, "rank": 1}, ...]
    """
    all_characters = []
    
    for text in texts:
        characters = extract_character_names(text)
        all_characters.extend(characters)
    
    # 대소문자 통일하여 카운트
    normalized_counter = Counter()
    original_names = {}  # 원래 이름 저장 (가장 많이 사용된 형태)
    
    for char in all_characters:
        key = char.lower()
        normalized_counter[key] += 1
        
        # 가장 많이 사용된 원래 형태 저장
        if key not in original_names:
            original_names[key] = Counter()
        original_names[key][char] += 1
    
    # 랭킹 생성
    rankings = []
    for rank, (key, mentions) in enumerate(normalized_counter.most_common(top_n), 1):
        # 가장 많이 사용된 원래 이름 형태
        original_name = original_names[key].most_common(1)[0][0]
        
        rankings.append({
            "name": original_name,
            "mentions": mentions,
            "rank": rank
        })
    
    return rankings


def analyze_character_trends(
    current_texts: List[str],
    previous_texts: List[str],
    top_n: int = 20
) -> List[Dict[str, any]]:
    """
    캐릭터 언급 트렌드 분석 (이전 기간 대비)
    
    Args:
        current_texts: 현재 기간 텍스트
        previous_texts: 이전 기간 텍스트
        top_n: 반환할 상위 개수
        
    Returns:
        [{"name": "캐릭터명", "current": 10, "previous": 5, "change": 100.0, "trend": "up"}, ...]
    """
    current_rankings = {r["name"].lower(): r["mentions"] for r in rank_characters(current_texts, top_n * 2)}
    previous_rankings = {r["name"].lower(): r["mentions"] for r in rank_characters(previous_texts, top_n * 2)}
    
    all_characters = set(current_rankings.keys()) | set(previous_rankings.keys())
    
    trends = []
    for char in all_characters:
        current = current_rankings.get(char, 0)
        previous = previous_rankings.get(char, 0)
        
        # 변화율 계산
        if previous > 0:
            change = ((current - previous) / previous) * 100
        elif current > 0:
            change = 100.0  # 새로 등장
        else:
            change = 0.0
        
        # 트렌드 방향
        if change > 10:
            trend = "up"
        elif change < -10:
            trend = "down"
        else:
            trend = "stable"
        
        trends.append({
            "name": char,
            "current": current,
            "previous": previous,
            "change": round(change, 1),
            "trend": trend
        })
    
    # 현재 언급 수 기준 정렬
    trends.sort(key=lambda x: x["current"], reverse=True)
    
    return trends[:top_n]


def detect_new_characters(
    current_texts: List[str],
    historical_characters: set
) -> List[Dict[str, any]]:
    """
    새로 등장한 캐릭터 감지
    
    Args:
        current_texts: 현재 기간 텍스트
        historical_characters: 이전에 등장했던 캐릭터 이름 집합
        
    Returns:
        [{"name": "캐릭터명", "mentions": 10, "is_new": True}, ...]
    """
    current_rankings = rank_characters(current_texts, 50)
    
    historical_lower = {c.lower() for c in historical_characters}
    
    new_characters = []
    for ranking in current_rankings:
        is_new = ranking["name"].lower() not in historical_lower
        if is_new:
            new_characters.append({
                "name": ranking["name"],
                "mentions": ranking["mentions"],
                "is_new": True
            })
    
    return new_characters
