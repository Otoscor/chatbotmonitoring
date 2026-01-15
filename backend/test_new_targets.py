"""
새로운 크롤링 대상 사이트 테스트
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

TARGETS = [
    {
        "name": "뤼튼 마이너갤",
        "url": "https://gall.dcinside.com/mgallery/board/lists/?id=wrtnai&page=1",
        "type": "dcinside_minor"
    },
    {
        "name": "AI챗팅 마이너갤",
        "url": "https://gall.dcinside.com/mgallery/board/lists/?id=aichatting&page=1",
        "type": "dcinside_minor"
    },
    {
        "name": "아카라이브 캐릭터AI",
        "url": "https://arca.live/b/characterai?p=1",
        "type": "arcalive"
    }
]

async def test_site(target):
    print(f"\n{'='*70}")
    print(f"테스트: {target['name']}")
    print(f"URL: {target['url']}")
    print(f"타입: {target['type']}")
    print('='*70)
    
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(target['url'], headers=headers, timeout=10.0)
            
            print(f"응답 코드: {response.status_code}")
            print(f"콘텐츠 크기: {len(response.text)} bytes")
            
            # 폐쇄 여부 확인
            if "폐쇄되었습니다" in response.text:
                print("❌ 갤러리가 폐쇄되었습니다")
                return False
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            if target['type'].startswith('dcinside'):
                # 디시인사이드 게시글 행 찾기
                rows = soup.select("tr.ub-content")
                print(f"발견된 게시글 행: {len(rows)}개")
                
                if rows:
                    # 첫 게시글 확인
                    first = rows[0]
                    num_elem = first.select_one("td.gall_num")
                    title_elem = first.select_one("td.gall_tit a")
                    
                    if num_elem and title_elem:
                        num = num_elem.get_text(strip=True)
                        title = title_elem.get_text(strip=True)
                        print(f"예시 게시글: [{num}] {title[:50]}")
                        print("✅ 크롤링 가능")
                        return True
                    
            elif target['type'] == 'arcalive':
                # 아카라이브 게시글 찾기
                articles = soup.select("a.vrow")
                print(f"발견된 게시글: {len(articles)}개")
                
                if articles:
                    first = articles[0]
                    title_elem = first.select_one(".title")
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        print(f"예시 게시글: {title[:50]}")
                        print("✅ 크롤링 가능")
                        return True
            
            print("⚠️  게시글을 찾을 수 없습니다")
            
            # HTML 일부 저장 (디버깅용)
            debug_file = f"/tmp/test_{target['type']}.html"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"→ HTML 저장: {debug_file}")
            
            return False
            
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False

async def main():
    print("=" * 70)
    print("크롤링 대상 사이트 테스트")
    print("=" * 70)
    
    results = []
    for target in TARGETS:
        result = await test_site(target)
        results.append((target['name'], result))
        await asyncio.sleep(1)  # Rate limiting
    
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    for name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{status} - {name}")

asyncio.run(main())
