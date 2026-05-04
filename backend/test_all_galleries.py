"""
모든 AI 관련 갤러리 상태 확인
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

GALLERIES = [
    ("ai", "AI 갤러리"),
    ("aibot", "AI봇 갤러리"),
    ("chatgpt", "ChatGPT 갤러리"),
    ("programming", "프로그래밍 갤러리"),
    ("game_dev", "게임 개발 갤러리"),
]

async def test_gallery(gallery_id: str, name: str):
    url = f"https://gall.dcinside.com/board/lists?id={gallery_id}&page=1"
    
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            
            # 폐쇄 메시지 확인
            if "폐쇄되었습니다" in response.text or "돌아갑니다" in response.text:
                print(f"❌ {name} ({gallery_id}) - 폐쇄됨")
                return False
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 게시글 행 찾기
            rows = soup.select("tr.ub-content")
            
            if rows and len(rows) > 0:
                print(f"✅ {name} ({gallery_id}) - 작동 ({len(rows)}개 게시글)")
                
                # 첫 게시글 제목
                first_title = rows[0].select_one("td.gall_tit a")
                if first_title:
                    print(f"   예시: {first_title.get_text(strip=True)[:50]}")
                return True
            else:
                print(f"⚠️  {name} ({gallery_id}) - HTML 구조 다름")
                return False
                
    except Exception as e:
        print(f"❌ {name} ({gallery_id}) - 에러: {e}")
        return False

async def main():
    print("=" * 70)
    print("디시인사이드 갤러리 상태 확인")
    print("=" * 70)
    print()
    
    working_galleries = []
    
    for gallery_id, name in GALLERIES:
        result = await test_gallery(gallery_id, name)
        if result:
            working_galleries.append((gallery_id, name))
        await asyncio.sleep(1)  # Rate limiting
        print()
    
    print("=" * 70)
    print(f"작동하는 갤러리: {len(working_galleries)}개")
    print("=" * 70)
    for gallery_id, name in working_galleries:
        print(f"  • {name} (id={gallery_id})")

asyncio.run(main())
