"""
신규 캐릭터챗 서비스 초기 데이터 삽입 스크립트
2025-2026년 런칭한 한국 캐릭터챗 서비스들을 데이터베이스에 추가합니다.
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from models.database import init_db, get_db_session, NewChatService


# 신규 서비스 데이터
NEW_SERVICES = [
    {
        "service_name": "제타",
        "service_name_en": "Zeta",
        "service_type": "web",
        "description": "한국형 AI 캐릭터 챗봇 플랫폼. 다양한 캐릭터와 자유로운 대화를 나눌 수 있으며, 사용자가 직접 캐릭터를 제작할 수 있습니다.",
        "launch_date": datetime(2024, 6, 1),
        "web_url": "https://zeta.zettamind.com",
        "ios_url": None,
        "android_url": None,
        "logo_url": None,
        "features": ["한국어 특화", "캐릭터 제작", "커뮤니티", "무료 이용"],
        "status": "active"
    },
    {
        "service_name": "베이비챗",
        "service_name_en": "BabeChat",
        "service_type": "web",
        "description": "성인 지향 AI 캐릭터 채팅 서비스. 다양한 페르소나를 가진 AI와 자유로운 대화가 가능합니다.",
        "launch_date": datetime(2024, 8, 15),
        "web_url": "https://babechat.io",
        "ios_url": None,
        "android_url": None,
        "logo_url": None,
        "features": ["성인 콘텐츠", "다양한 캐릭터", "실시간 대화", "이미지 생성"],
        "status": "active"
    },
    {
        "service_name": "크랙",
        "service_name_en": "Crack",
        "service_type": "web",
        "description": "역할극과 스토리텔링에 특화된 AI 캐릭터 플랫폼. 몰입감 있는 시나리오 기반 대화를 제공합니다.",
        "launch_date": datetime(2024, 3, 20),
        "web_url": "https://crack.so",
        "ios_url": None,
        "android_url": None,
        "logo_url": None,
        "features": ["역할극", "스토리 모드", "시나리오 생성", "다중 캐릭터"],
        "status": "active"
    },
    {
        "service_name": "루나톡",
        "service_name_en": "LunaTalk",
        "service_type": "web",
        "description": "감성적인 대화에 특화된 AI 친구 서비스. 일상의 고민을 나누고 위로받을 수 있습니다.",
        "launch_date": datetime(2024, 10, 1),
        "web_url": "https://lunatalk.ai",
        "ios_url": None,
        "android_url": None,
        "logo_url": None,
        "features": ["감성 대화", "일기 기능", "심리 상담", "장기 기억"],
        "status": "active"
    },
    {
        "service_name": "캐릭터AI",
        "service_name_en": "Character.AI",
        "service_type": "both",
        "description": "세계 최대 AI 캐릭터 플랫폼. 수백만 개의 캐릭터와 대화하고, 나만의 캐릭터를 만들 수 있습니다.",
        "launch_date": datetime(2022, 9, 16),
        "web_url": "https://beta.character.ai",
        "ios_url": "https://apps.apple.com/us/app/character-ai-ai-chat/id6447946071",
        "android_url": "https://play.google.com/store/apps/details?id=ai.character.app",
        "logo_url": None,
        "features": ["수백만 캐릭터", "커뮤니티", "음성 대화", "그룹 채팅"],
        "status": "active"
    },
    {
        "service_name": "스파이시챗",
        "service_name_en": "SpicyChat",
        "service_type": "web",
        "description": "성인 콘텐츠 특화 AI 캐릭터 채팅 플랫폼. 제한 없는 대화와 다양한 시나리오를 제공합니다.",
        "launch_date": datetime(2023, 5, 1),
        "web_url": "https://spicychat.ai",
        "ios_url": None,
        "android_url": None,
        "logo_url": None,
        "features": ["성인 콘텐츠", "무제한 대화", "이미지 생성", "커스텀 캐릭터"],
        "status": "active"
    },
    {
        "service_name": "잰디",
        "service_name_en": "Janitor AI",
        "service_type": "web",
        "description": "커스터마이징 가능한 AI 캐릭터 플랫폼. 다양한 LLM 모델을 선택하여 사용할 수 있습니다.",
        "launch_date": datetime(2023, 6, 1),
        "web_url": "https://janitorai.com",
        "ios_url": None,
        "android_url": None,
        "logo_url": None,
        "features": ["다양한 LLM", "캐릭터 제작", "API 지원", "커뮤니티"],
        "status": "active"
    }
]


async def insert_new_services():
    """신규 서비스 데이터를 데이터베이스에 삽입"""
    # 데이터베이스 초기화
    await init_db()
    
    async with get_db_session() as session:
        # 기존 데이터 확인
        result = await session.execute(select(NewChatService))
        existing_services = result.scalars().all()
        
        if existing_services:
            print(f"⚠️  이미 {len(existing_services)}개의 서비스가 등록되어 있습니다.")
            response = input("기존 데이터를 삭제하고 다시 삽입하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                for service in existing_services:
                    await session.delete(service)
                await session.commit()
                print("✅ 기존 데이터 삭제 완료")
            else:
                print("❌ 작업을 취소했습니다.")
                return
        
        # 새 데이터 삽입
        inserted_count = 0
        for service_data in NEW_SERVICES:
            service = NewChatService(**service_data)
            session.add(service)
            inserted_count += 1
            print(f"  → {service_data['service_name']} ({service_data['service_name_en']}) 추가")
        
        await session.commit()
        print(f"\n✅ 총 {inserted_count}개의 신규 서비스가 등록되었습니다!")


async def list_services():
    """등록된 서비스 목록 출력"""
    async with get_db_session() as session:
        result = await session.execute(
            select(NewChatService).order_by(NewChatService.launch_date)
        )
        services = result.scalars().all()
        
        if not services:
            print("등록된 서비스가 없습니다.")
            return
        
        print(f"\n📋 등록된 신규 캐릭터챗 서비스 ({len(services)}개)\n")
        print("-" * 80)
        for i, service in enumerate(services, 1):
            print(f"{i}. {service.service_name} ({service.service_name_en})")
            print(f"   타입: {service.service_type} | 상태: {service.status}")
            print(f"   런칭: {service.launch_date.strftime('%Y-%m-%d')}")
            print(f"   설명: {service.description[:50]}...")
            print("-" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        # 목록 조회
        asyncio.run(list_services())
    else:
        # 데이터 삽입
        asyncio.run(insert_new_services())
