import httpx
import asyncio

async def debug():
    url = "https://api.zeta-ai.io/v1/plots/ranking"
    params = {
        "limit": 30,
        "genres": "ALL",
        "type": "TRENDING",
        "filterType": "GENRE",
        "filterValues": "all"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://zeta-ai.io/",
        "Origin": "https://zeta-ai.io"
    }
    
    async with httpx.AsyncClient() as client:
        print(f"Requesting {url} with params {params}")
        resp = await client.get(url, params=params, headers=headers)
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            print("Response Keys:", data.keys())
            rankings = data.get("rankings", [])
            print(f"Rankings count: {len(rankings)}")
            if rankings:
                print("First item:", rankings[0])
            else:
                 print("Raw response:", resp.text[:500])
        except Exception as e:
            print("Error parsing JSON:", e)
            print("Raw text:", resp.text[:500])

if __name__ == "__main__":
    asyncio.run(debug())
