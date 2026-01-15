"""
아카라이브 크롤러
"""
import asyncio
import re
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
import logging

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CrawledPost:
    """크롤링된 게시글 데이터"""
    post_id: str
    gallery_id: str
    title: str
    author: Optional[str]
    created_at: Optional[datetime]
    view_count: int
    recommend_count: int
    comment_count: int
    url: str


class ArcaliveCrawler:
    """아카라이브 크롤러"""
    
    BASE_URL = "https://arca.live"
    
    def __init__(self, board_id: str = "characterai"):
        self.settings = get_settings()
        self.board_id = board_id
        self.ua = UserAgent()
        self.delay = self.settings.crawl_delay_seconds
        self.max_retries = 3
        
    def _get_headers(self):
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html",
        }
    
    async def _fetch_page(self, url: str, client: httpx.AsyncClient) -> Optional[str]:
        """페이지 HTML 가져오기"""
        for attempt in range(self.max_retries):
            try:
                response = await client.get(url, headers=self._get_headers(), timeout=30.0)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"요청 에러 (시도 {attempt + 1}/{self.max_retries}): {e}")
                await asyncio.sleep(self.delay * (attempt + 1))
        return None
    
    def _parse_post_list(self, html: str) -> List[CrawledPost]:
        """게시글 목록 파싱"""
        posts = []
        soup = BeautifulSoup(html, "html.parser")
        
        # 게시글 찾기
        vrows = soup.select("a.vrow")
        logger.info(f"HTML에서 {len(vrows)}개 행 발견")
        
        for vrow in vrows:
            try:
                # 공지사항 제외
                if 'notice' in vrow.get('class', []):
                    continue
                
                # 게시글 ID
                href = vrow.get('href', '')
                match = re.search(r'/(\d+)\?', href)
                if not match:
                    continue
                post_id = match.group(1)
                
                # 제목
                title_elem = vrow.select_one(".title")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # URL
                url = f"{self.BASE_URL}{href}" if href.startswith('/') else href
                
                # 작성자
                author_elem = vrow.select_one(".user-info")
                author = author_elem.get_text(strip=True) if author_elem else None
                
                # 작성일
                time_elem = vrow.select_one("time")
                created_at = None
                if time_elem:
                    time_str = time_elem.get_text(strip=True)
                    created_at = self._parse_date(time_str)
                
                # 조회수
                view_elem = vrow.select_one(".vcol-hits, .col-rate")
                view_count = 0
                if view_elem:
                    view_text = view_elem.get_text(strip=True)
                    view_match = re.search(r'\d+', view_text)
                    if view_match:
                        view_count = int(view_match.group())
                
                # 추천수
                rate_elem = vrow.select_one(".vcol-rate")
                recommend_count = 0
                if rate_elem:
                    rate_text = rate_elem.get_text(strip=True)
                    rate_match = re.search(r'\d+', rate_text)
                    if rate_match:
                        recommend_count = int(rate_match.group())
                
                # 댓글수
                comment_elem = vrow.select_one(".vcol-comment")
                comment_count = 0
                if comment_elem:
                    comment_text = comment_elem.get_text(strip=True)
                    comment_match = re.search(r'\d+', comment_text)
                    if comment_match:
                        comment_count = int(comment_match.group())
                
                posts.append(CrawledPost(
                    post_id=post_id,
                    gallery_id=self.board_id,
                    title=title,
                    author=author,
                    created_at=created_at,
                    view_count=view_count,
                    recommend_count=recommend_count,
                    comment_count=comment_count,
                    url=url
                ))
                
            except Exception as e:
                logger.warning(f"게시글 파싱 에러: {e}")
                continue
        
        return posts
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열 파싱"""
        if not date_str:
            return None
        
        try:
            # "2026.01.14" 형식
            if re.match(r'\d{4}\.\d{2}\.\d{2}', date_str):
                return datetime.strptime(date_str, "%Y.%m.%d")
        except ValueError:
            pass
        
        return None
    
    async def crawl_board(self, pages: int = None) -> List[CrawledPost]:
        """게시판 크롤링"""
        pages = pages or self.settings.max_pages_per_crawl
        all_posts = []
        
        logger.info(f"크롤링 시작: 게시판={self.board_id}, 페이지 수={pages}")
        
        async with httpx.AsyncClient() as client:
            for page in range(1, pages + 1):
                url = f"{self.BASE_URL}/b/{self.board_id}?p={page}"
                
                logger.info(f"페이지 {page}/{pages} 크롤링 중...")
                html = await self._fetch_page(url, client)
                
                if html:
                    posts = self._parse_post_list(html)
                    all_posts.extend(posts)
                    logger.info(f"페이지 {page}에서 {len(posts)}개 게시글 수집")
                else:
                    logger.warning(f"페이지 {page} 크롤링 실패")
                
                if page < pages:
                    await asyncio.sleep(self.delay)
        
        logger.info(f"크롤링 완료: 총 {len(all_posts)}개 게시글 수집")
        return all_posts
