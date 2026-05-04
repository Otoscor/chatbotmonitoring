
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from models.database import AsyncSessionLocal, ChatServiceCharacter
from crawler.character_service_crawler import crawl_all_character_services

async def run_manual_character_crawl():
    print("🤖 캐릭터 서비스 수동 크롤링 시작...")
    
    # 1. 크롤링 실행 (자원 절약을 위해 필요한 것만 or 전체)
    # 모든 서비스 크롤링하여 데이터 일관성 유지
    # target_services = ['caveduck', 'elyn'] 
    target_services = None # None이면 전체 서비스 (zeta, babechat, lunatalk, crack, elyn, caveduck)
    results = await crawl_all_character_services(services=target_services)
    
    async with AsyncSessionLocal() as session:
        for service, characters in results.items():
            if not characters:
                print(f"⚠️  {service}: 수집된 데이터가 없습니다.")
                continue
                
            print(f"✅ {service}: {len(characters)}개 데이터 DB 저장 중...")
            
            # 기존 해당 서비스 데이터 삭제 (또는 업데이트 전략)
            # 랭킹 데이터이므로 기존 데이터를 지우고 새로 넣는 것이 깔끔함 (또는 crawled_at으로 구분)
            # 여기서는 최근 데이터만 유효하므로, 해당 서비스의 데이터를 모두 지우거나, 
            # 아니면 그냥 추가하고 export에서 시간으로 필터링.
            # export 로직은 '최근 크롤링 시간' 기준 5분 이내 데이터를 가져옴.
            # 따라서 그냥 추가하면 됨.
            
            for char_data in characters:
                db_char = ChatServiceCharacter(
                    service=service,
                    character_id=char_data.character_id,
                    rank=char_data.rank,
                    name=char_data.name,
                    author=char_data.author,
                    views=char_data.views,
                    tags=char_data.tags,
                    description=char_data.description,
                    thumbnail_url=char_data.thumbnail_url,
                    character_url=char_data.character_url,
                    crawled_at=datetime.utcnow()
                )
                session.add(db_char)
            
            await session.commit()
            print(f"  ✓ {service} 저장 완료")
            
    print("✨ 모든 캐릭터 데이터 처리 완료")

if __name__ == "__main__":
    asyncio.run(run_manual_character_crawl())
