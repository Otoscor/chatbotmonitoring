"""
HTML 파싱 유틸리티
"""
import re
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class ParsedContent:
    """파싱된 콘텐츠"""
    text: str
    images: List[str]
    links: List[str]


def clean_text(text: str) -> str:
    """텍스트 정제"""
    if not text:
        return ""
    
    # 연속된 공백 제거
    text = re.sub(r"\s+", " ", text)
    # 앞뒤 공백 제거
    text = text.strip()
    # 특수 문자 정규화
    text = re.sub(r"[​\u200b\u200c\u200d\ufeff]", "", text)
    
    return text


def extract_text_from_html(html: str) -> str:
    """HTML에서 텍스트만 추출"""
    if not html:
        return ""
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 스크립트, 스타일 태그 제거
    for tag in soup(["script", "style", "iframe", "noscript"]):
        tag.decompose()
    
    text = soup.get_text(separator=" ")
    return clean_text(text)


def parse_post_content(html: str) -> ParsedContent:
    """게시글 본문 파싱"""
    if not html:
        return ParsedContent(text="", images=[], links=[])
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 이미지 추출
    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and not src.startswith("data:"):
            images.append(src)
    
    # 링크 추출
    links = []
    for a in soup.find_all("a"):
        href = a.get("href")
        if href and href.startswith("http"):
            links.append(href)
    
    # 텍스트 추출
    text = extract_text_from_html(html)
    
    return ParsedContent(text=text, images=images, links=links)


def extract_character_names(text: str) -> List[str]:
    """
    텍스트에서 캐릭터 이름 추출
    - 대괄호 안의 텍스트: [캐릭터명]
    - 따옴표 안의 텍스트: "캐릭터명"
    - 특정 패턴: ~봇, ~bot 등
    """
    character_names = []
    
    # 대괄호 패턴: [캐릭터명]
    bracket_pattern = re.findall(r"\[([^\]]+)\]", text)
    character_names.extend(bracket_pattern)
    
    # 따옴표 패턴: "캐릭터명"
    quote_pattern = re.findall(r'"([^"]+)"', text)
    character_names.extend(quote_pattern)
    
    # 봇 패턴: xxx봇, xxxbot
    bot_pattern = re.findall(r"([가-힣a-zA-Z0-9]+(?:봇|bot|Bot))", text)
    character_names.extend(bot_pattern)
    
    # 중복 제거 및 정제
    cleaned_names = []
    for name in character_names:
        name = clean_text(name)
        if name and len(name) >= 2 and len(name) <= 50:
            cleaned_names.append(name)
    
    return list(set(cleaned_names))
