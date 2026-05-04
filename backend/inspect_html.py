"""
HTML 구조 상세 분석
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

async def inspect():
    url = "https://gall.dcinside.com/board/lists?id=programming&page=1"
    
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=10.0)
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        print("=" * 70)
        print("HTML 구조 분석 - programming 갤러리")
        print("=" * 70)
        
        # 1. tr.ub-content 찾기
        rows = soup.select("tr.ub-content")
        print(f"\n1. tr.ub-content 찾기: {len(rows)}개")
        
        if rows:
            print(f"\n첫 번째 게시글 행:")
            first_row = rows[0]
            print(f"  클래스: {first_row.get('class', [])}")
            
            # 각 필드 확인
            print(f"\n  필드 확인:")
            print(f"    - td.gall_num: {first_row.select_one('td.gall_num')}")
            print(f"    - td.gall_tit: {first_row.select_one('td.gall_tit')}")
            print(f"    - td.gall_writer: {first_row.select_one('td.gall_writer')}")
            print(f"    - td.gall_count: {first_row.select_one('td.gall_count')}")
            
            # 전체 HTML 구조
            print(f"\n  첫 번째 행 HTML:")
            print("  " + "-" * 65)
            print(f"  {first_row.prettify()[:500]}")
            print("  " + "-" * 65)
        else:
            print("  ❌ tr.ub-content를 찾지 못했습니다!")
            
            # 대안 찾기
            print("\n2. 대안 찾기:")
            
            # 모든 tr 태그
            all_trs = soup.find_all("tr")
            print(f"  - 전체 tr 태그: {len(all_trs)}개")
            
            if all_trs:
                print(f"\n  첫 3개 tr의 클래스:")
                for i, tr in enumerate(all_trs[:3], 1):
                    classes = tr.get('class', ['없음'])
                    print(f"    {i}. {classes}")

asyncio.run(inspect())
