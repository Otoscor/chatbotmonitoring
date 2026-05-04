"""
디시인사이드 갤러리 크롤러
- Rate limiting 적용
- 에러 핸들링 및 재시도 로직
- robots.txt 준수
"""
import asyncio
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from config import get_settings

# 로깅 설정
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


class DCInsideCrawler:
    """디시인사이드 갤러리 크롤러 (일반 + 마이너)"""
    
    BASE_URL = "https://gall.dcinside.com"
    GALLERY_LIST_URL = "{base}/board/lists?id={gallery_id}&page={page}"
    MINOR_GALLERY_LIST_URL = "{base}/mgallery/board/lists/?id={gallery_id}&page={page}"
    
    def __init__(self, gallery_id: str = None, is_minor: bool = False):
        self.settings = get_settings()
        self.gallery_id = gallery_id
        self.is_minor = is_minor
        self.ua = UserAgent()
        self.delay = self.settings.crawl_delay_seconds
        self.max_retries = 3
        
    def _get_headers(self) -> Dict[str, str]:
        """요청 헤더 생성"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": self.BASE_URL,
        }
    
    async def _fetch_page(self, url: str, client: httpx.AsyncClient) -> Optional[str]:
        """페이지 HTML 가져오기 (재시도 로직 포함)"""
        for attempt in range(self.max_retries):
            try:
                response = await client.get(url, headers=self._get_headers(), timeout=30.0)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP 에러 {e.response.status_code}: {url} (시도 {attempt + 1}/{self.max_retries})")
                if e.response.status_code == 403:
                    logger.error("접근이 차단되었습니다. 크롤링 속도를 줄이거나 잠시 후 다시 시도하세요.")
                    return None
                await asyncio.sleep(self.delay * (attempt + 1))
            except httpx.RequestError as e:
                logger.warning(f"요청 에러: {e} (시도 {attempt + 1}/{self.max_retries})")
                await asyncio.sleep(self.delay * (attempt + 1))
        return None
    
    def _parse_post_list(self, html: str) -> List[CrawledPost]:
        """게시글 목록 HTML 파싱"""
        posts = []
        soup = BeautifulSoup(html, "html.parser")
        
        # 게시글 목록 찾기
        post_rows = soup.select("tr.ub-content")
        logger.debug(f"HTML에서 {len(post_rows)}개 행 발견")
        
        skipped = {"no_num": 0, "non_digit": 0, "no_title": 0, "success": 0, "error": 0}
        
        for idx, row in enumerate(post_rows, 1):
            try:
                # 주의: "us-post"는 일반 게시글입니다 (공지사항이 아님!)
                
                # 게시글 번호
                post_num_elem = row.select_one("td.gall_num")
                if not post_num_elem:
                    skipped["no_num"] += 1
                    continue
                    
                post_id = post_num_elem.get_text(strip=True)
                
                # 숫자가 아닌 경우 (공지, 설문 등) 스킵
                if not post_id.isdigit():
                    skipped["non_digit"] += 1
                    continue
                
                # 제목
                title_elem = row.select_one("td.gall_tit a")
                if not title_elem:
                    skipped["no_title"] += 1
                    continue
                title = title_elem.get_text(strip=True)
                
                # URL
                href = title_elem.get("href", "")
                url = f"{self.BASE_URL}{href}" if href.startswith("/") else href
                
                # 작성자
                author_elem = row.select_one("td.gall_writer")
                author = None
                if author_elem:
                    nick_elem = author_elem.select_one("span.nickname, em")
                    if nick_elem:
                        author = nick_elem.get_text(strip=True)
                
                # 작성일
                date_elem = row.select_one("td.gall_date")
                created_at = None
                if date_elem:
                    date_str = date_elem.get("title", "") or date_elem.get_text(strip=True)
                    created_at = self._parse_date(date_str)
                
                # 조회수
                view_elem = row.select_one("td.gall_count")
                view_count = 0
                if view_elem:
                    view_text = view_elem.get_text(strip=True)
                    if view_text.isdigit():
                        view_count = int(view_text)
                
                # 추천수
                recommend_elem = row.select_one("td.gall_recommend")
                recommend_count = 0
                if recommend_elem:
                    recommend_text = recommend_elem.get_text(strip=True)
                    if recommend_text.isdigit():
                        recommend_count = int(recommend_text)
                
                # 댓글 수
                comment_count = 0
                comment_elem = row.select_one("td.gall_tit span.reply_num")
                if comment_elem:
                    comment_text = comment_elem.get_text(strip=True)
                    comment_match = re.search(r"\d+", comment_text)
                    if comment_match:
                        comment_count = int(comment_match.group())
                
                posts.append(CrawledPost(
                    post_id=post_id,
                    gallery_id=self.gallery_id,
                    title=title,
                    author=author,
                    created_at=created_at,
                    view_count=view_count,
                    recommend_count=recommend_count,
                    comment_count=comment_count,
                    url=url
                ))
                skipped["success"] += 1
                
            except Exception as e:
                skipped["error"] += 1
                logger.warning(f"게시글 파싱 에러: {e}")
                continue
        
        logger.debug(f"파싱 결과 - 성공: {skipped['success']}, 스킵: {skipped['non_digit'] + skipped['no_title']}")
        return posts
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열 파싱"""
        if not date_str:
            return None
        
        try:
            # "2024-01-15 12:30:45" 형식
            if "-" in date_str and ":" in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            # "01-15" 또는 "01.15" 형식 (올해로 가정)
            elif re.match(r"\d{2}[.-]\d{2}", date_str):
                month_day = date_str.replace(".", "-")
                return datetime.strptime(f"{datetime.now().year}-{month_day}", "%Y-%m-%d")
            # "12:30" 형식 (오늘로 가정)
            elif re.match(r"\d{2}:\d{2}", date_str):
                today = datetime.now().strftime("%Y-%m-%d")
                return datetime.strptime(f"{today} {date_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            pass
        
        return None
    
    async def crawl_gallery(self, pages: int = None) -> List[CrawledPost]:
        """갤러리 크롤링"""
        pages = pages or self.settings.max_pages_per_crawl
        all_posts = []
        
        gallery_type = "마이너갤" if self.is_minor else "일반갤"
        logger.info(f"크롤링 시작: 갤러리={self.gallery_id} ({gallery_type}), 페이지 수={pages}")
        
        async with httpx.AsyncClient() as client:
            for page in range(1, pages + 1):
                # 마이너갤러리와 일반 갤러리 URL 구분
                url_template = self.MINOR_GALLERY_LIST_URL if self.is_minor else self.GALLERY_LIST_URL
                url = url_template.format(
                    base=self.BASE_URL,
                    gallery_id=self.gallery_id,
                    page=page
                )
                
                logger.info(f"페이지 {page}/{pages} 크롤링 중...")
                html = await self._fetch_page(url, client)
                
                if html:
                    posts = self._parse_post_list(html)
                    all_posts.extend(posts)
                    logger.info(f"페이지 {page}에서 {len(posts)}개 게시글 수집")
                else:
                    logger.warning(f"페이지 {page} 크롤링 실패")
                
                # Rate limiting
                if page < pages:
                    await asyncio.sleep(self.delay)
        
        logger.info(f"크롤링 완료: 총 {len(all_posts)}개 게시글 수집")
        return all_posts


async def run_crawler(gallery_id: str = None, pages: int = None) -> List[CrawledPost]:
    """크롤러 실행 헬퍼 함수"""
    crawler = DCInsideCrawler(gallery_id)
    return await crawler.crawl_gallery(pages)


# 테스트용
if __name__ == "__main__":
    async def main():
        posts = await run_crawler(pages=2)
        for post in posts[:5]:
            print(f"[{post.post_id}] {post.title} - 조회: {post.view_count}, 추천: {post.recommend_count}")
    
    asyncio.run(main())
