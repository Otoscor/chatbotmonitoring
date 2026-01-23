"""
데이터베이스 테이블 생성 스크립트
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from models.database import init_db


async def create_tables():
    """모든 테이블 생성"""
    print("데이터베이스 테이블 생성 중...")
    await init_db()
    print("✅ 테이블 생성 완료")


if __name__ == "__main__":
    asyncio.run(create_tables())
