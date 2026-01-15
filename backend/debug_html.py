"""
실제 HTML 구조 확인
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

async def fetch_html():
    url = "https://gall.dcinside.com/board/lists?id=chatbot&page=1"
    
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=10.0)
        
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        print(f"Content-Length: {len(response.text)}")
        print("\n" + "="*60)
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 게시글 행 찾기 시도
        print("\n1. 'tr.ub-content' 찾기:")
        rows = soup.select("tr.ub-content")
        print(f"   발견: {len(rows)}개")
        
        print("\n2. 'tr' 태그 전체 찾기:")
        all_trs = soup.find_all("tr")
        print(f"   발견: {len(all_trs)}개")
        if all_trs:
            print(f"   첫 번째 tr의 클래스: {all_trs[0].get('class', [])}")
        
        print("\n3. 게시판 관련 클래스 찾기:")
        classes_to_try = [
            "gall_list",
            "ub-content",
            "us-post",
            "list-tr",
            "article-list",
        ]
        for cls in classes_to_try:
            elements = soup.find_all(class_=cls)
            print(f"   .{cls}: {len(elements)}개")
        
        print("\n4. HTML 일부 출력 (처음 2000자):")
        print("-" * 60)
        print(response.text[:2000])
        print("-" * 60)
        
        # HTML 전체를 파일로 저장
        with open("/tmp/dcinside_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("\n✅ 전체 HTML을 /tmp/dcinside_page.html 에 저장했습니다.")

asyncio.run(fetch_html())
