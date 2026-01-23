"""
구글 뉴스 RSS 크롤러
RSS 피드를 통해 무료로 뉴스 수집
"""
import asyncio
import hashlib
import re
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from urllib.parse import quote
import logging

import httpx
from bs4 import BeautifulSoup

from config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class NewsArticleData:
    """뉴스 기사 데이터"""
    article_id: str
    source: str  # 'google'
    title: str
    description: Optional[str]
    url: str
    publisher: Optional[str]
    published_at: Optional[datetime]
    keyword: str


class GoogleNewsCrawler:
    """구글 뉴스 RSS 크롤러"""
    
    RSS_BASE_URL = "https://news.google.com/rss/search"
    
    def __init__(self):
        self.delay = 1.0  # 요청 간 딜레이
    
    def _generate_article_id(self, url: str) -> str:
        """URL 기반 고유 ID 생성"""
        return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        # HTML 태그 제거
        clean = re.sub(r'<[^>]+>', '', text)
        return clean.strip()
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """RSS 날짜 형식 파싱"""
        if not date_str:
            return None
        try:
            # "Thu, 16 Jan 2025 03:15:00 GMT" 형식
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return None
    
    def _extract_publisher(self, title: str) -> tuple:
        """제목에서 언론사 추출 (구글 뉴스 형식: "제목 - 언론사")"""
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return title, None
    
    async def search_news(self, keyword: str, limit: int = 20) -> List[NewsArticleData]:
        """
        구글 뉴스 RSS로 검색
        
        Args:
            keyword: 검색 키워드
            limit: 최대 결과 개수
        
        Returns:
            뉴스 기사 목록
        """
        # RSS URL 생성 (한국어, 한국 지역)
        encoded_keyword = quote(keyword)
        rss_url = f"{self.RSS_BASE_URL}?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(rss_url, headers=headers)
                response.raise_for_status()
                
                # RSS XML 파싱
                soup = BeautifulSoup(response.text, "xml")
                items = soup.find_all("item")
                
                articles = []
                for item in items[:limit]:
                    raw_title = item.find("title").text if item.find("title") else ""
                    title, publisher = self._extract_publisher(raw_title)
                    
                    link = item.find("link").text if item.find("link") else ""
                    pub_date = item.find("pubDate").text if item.find("pubDate") else ""
                    description = item.find("description").text if item.find("description") else ""
                    
                    # source 태그에서 언론사 정보 추출 (있는 경우)
                    source_tag = item.find("source")
                    if source_tag:
                        publisher = source_tag.text
                    
                    article = NewsArticleData(
                        article_id=self._generate_article_id(link),
                        source="google",
                        title=self._clean_text(title),
                        description=self._clean_text(description),
                        url=link,
                        publisher=publisher,
                        published_at=self._parse_date(pub_date),
                        keyword=keyword,
                    )
                    articles.append(article)
                
                logger.info(f"구글 뉴스 '{keyword}' 검색 완료: {len(articles)}개")
                return articles
                
        except httpx.HTTPStatusError as e:
            logger.error(f"구글 뉴스 HTTP 오류: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"구글 뉴스 검색 오류: {e}")
            return []
    
    async def crawl_all_keywords(self, keywords: List[str] = None, limit_per_keyword: int = 20) -> List[NewsArticleData]:
        """
        모든 키워드에 대해 뉴스 검색
        
        Args:
            keywords: 검색 키워드 목록 (None이면 설정에서 가져옴)
            limit_per_keyword: 키워드당 최대 결과 개수
        
        Returns:
            전체 뉴스 기사 목록
        """
        if keywords is None:
            settings = get_settings()
            keywords = settings.news_keywords
        
        all_articles = []
        seen_urls = set()
        
        for keyword in keywords:
            articles = await self.search_news(keyword, limit=limit_per_keyword)
            
            # 중복 제거
            for article in articles:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    all_articles.append(article)
            
            await asyncio.sleep(self.delay)
        
        logger.info(f"구글 뉴스 전체 크롤링 완료: {len(all_articles)}개 (중복 제거됨)")
        return all_articles
