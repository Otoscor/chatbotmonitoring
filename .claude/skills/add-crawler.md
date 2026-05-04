# /add-crawler - 새 크롤러 추가

새로운 데이터 소스에 대한 크롤러를 추가합니다.

---

## 사용법

```
/add-crawler <크롤러명> <사이트URL>
```

### 예시
```
/add-crawler charstar https://charstar.ai
```

---

## 크롤러 생성 가이드

### 1. 크롤러 파일 생성

위치: `backend/crawler/{크롤러명}_crawler.py`

### 2. 기본 템플릿

```python
"""
{사이트명} 크롤러
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from models.database import Post, get_session

class {크롤러명}Crawler:
    """
    {사이트명}에서 데이터를 수집하는 크롤러
    """

    BASE_URL = "{사이트URL}"

    def __init__(self):
        self.session: Session = get_session()

    async def crawl(self, max_pages: int = 5) -> List[Dict]:
        """
        게시글 크롤링

        Args:
            max_pages: 크롤링할 최대 페이지 수

        Returns:
            크롤링된 게시글 목록
        """
        results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                for page_num in range(1, max_pages + 1):
                    url = f"{self.BASE_URL}/page/{page_num}"
                    await page.goto(url, wait_until="networkidle")

                    # 게시글 목록 파싱
                    posts = await self._parse_posts(page)
                    results.extend(posts)

                    # 딜레이 (예의 바른 크롤링)
                    await asyncio.sleep(1)

            finally:
                await browser.close()

        return results

    async def _parse_posts(self, page) -> List[Dict]:
        """게시글 파싱 로직"""
        posts = []
        # TODO: 실제 파싱 로직 구현
        return posts

    def save_to_db(self, posts: List[Dict]) -> int:
        """데이터베이스에 저장"""
        saved_count = 0

        for post_data in posts:
            existing = self.session.query(Post).filter_by(
                source="{크롤러명}",
                external_id=post_data["id"]
            ).first()

            if not existing:
                post = Post(
                    title=post_data["title"],
                    content=post_data.get("content"),
                    source="{크롤러명}",
                    external_id=post_data["id"],
                    url=post_data["url"],
                    created_at=post_data.get("created_at", datetime.now())
                )
                self.session.add(post)
                saved_count += 1

        self.session.commit()
        return saved_count


async def main():
    crawler = {크롤러명}Crawler()
    posts = await crawler.crawl()
    saved = crawler.save_to_db(posts)
    print(f"크롤링 완료: {len(posts)}개 수집, {saved}개 저장")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. run_all.py에 등록

```python
# backend/crawler/run_all.py
from crawler.{크롤러명}_crawler import {크롤러명}Crawler

CRAWLERS = [
    # ... 기존 크롤러들
    {크롤러명}Crawler,
]
```

---

## 4. export_data.py 수정

새 소스의 데이터를 JSON으로 내보내도록 수정

---

## 크롤링 유형

### BeautifulSoup (정적 페이지)
```python
import requests
from bs4 import BeautifulSoup

response = requests.get(url, headers={"User-Agent": "..."})
soup = BeautifulSoup(response.text, "html.parser")
```

### Playwright (동적 페이지)
```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(url)
```

### RSS Feed
```python
import feedparser

feed = feedparser.parse(rss_url)
for entry in feed.entries:
    print(entry.title, entry.link)
```

---

## 체크리스트

- [ ] 크롤러 파일 생성
- [ ] 파싱 로직 구현
- [ ] DB 저장 로직 구현
- [ ] run_all.py에 등록
- [ ] export_data.py 수정
- [ ] 테스트 실행
- [ ] robots.txt 확인
