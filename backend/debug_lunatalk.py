import httpx
import asyncio

async def debug():
    url = "https://lunatalk.chat/character/api"
    payload = {
        "action": "rank_list",
        "offset": "23",
        "limit": "7",
        "period": "daily",
        "v": "1"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://lunatalk.chat",
        "Referer": "https://lunatalk.chat/character/rank"
    }
    
    async with httpx.AsyncClient() as client:
        print(f"Requesting {url} with payload {payload}")
        resp = await client.post(url, data=payload, headers=headers)
        print(f"Status: {resp.status_code}")
        print("Response Text Preview:")
        print(resp.text[:1000])

if __name__ == "__main__":
    asyncio.run(debug())
