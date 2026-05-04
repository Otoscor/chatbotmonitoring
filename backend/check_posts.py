"""
실제 게시글 구조 확인
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

async def check():
    url = "https://gall.dcinside.com/board/lists?id=programming&page=1"
    
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=10.0)
        soup = BeautifulSoup(response.text, "html.parser")
        
        rows = soup.select("tr.ub-content")
        print(f"총 {len(rows)}개 행 발견\n")
        
        print("첫 10개 행의 gall_num 확인:")
        print("=" * 70)
        
        normal_posts = []
        for i, row in enumerate(rows[:15], 1):
            num_elem = row.select_one("td.gall_num")
            if num_elem:
                num_text = num_elem.get_text(strip=True)
                title_elem = row.select_one("td.gall_tit a")
                title = title_elem.get_text(strip=True)[:40] if title_elem else "없음"
                
                status = "✅ 일반" if num_text.isdigit() else f"⏭️  {num_text}"
                print(f"{i}. [{num_text:>6}] {status} - {title}")
                
                if num_text.isdigit():
                    normal_posts.append(row)
        
        print(f"\n일반 게시글 수: {len(normal_posts)}개")
        
        if normal_posts:
            print("\n✅ 첫 번째 일반 게시글 상세:")
            print("-" * 70)
            post = normal_posts[0]
            
            num = post.select_one("td.gall_num").get_text(strip=True)
            title = post.select_one("td.gall_tit a").get_text(strip=True)
            href = post.select_one("td.gall_tit a").get("href", "")
            
            writer_elem = post.select_one("td.gall_writer")
            writer = writer_elem.get_text(strip=True) if writer_elem else "없음"
            
            count_elem = post.select_one("td.gall_count")
            count = count_elem.get_text(strip=True) if count_elem else "0"
            
            print(f"  번호: {num}")
            print(f"  제목: {title}")
            print(f"  작성자: {writer}")
            print(f"  조회수: {count}")
            print(f"  URL: {href}")
            
            print("\n✅ 크롤러가 정상 작동할 수 있습니다!")

asyncio.run(check())
