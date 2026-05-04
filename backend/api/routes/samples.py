"""
캐릭터 샘플 생성 API 라우트
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, ChatServiceCharacter
from api.schemas.samples import CharacterSampleRequest, CharacterSampleResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/character-samples/generate", response_model=CharacterSampleResponse)
async def generate_character_samples(
    request: CharacterSampleRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Gemini API를 사용하여 캐릭터 샘플 생성

    - **tag_combinations**: 각 샘플에 사용할 태그 조합 리스트
    """
    try:
        from utils.gemini_client import generate_character_samples as generate_samples

        all_samples = []

        for i, tags in enumerate(request.tag_combinations):
            # 참고할 인기 캐릭터 조회 (해당 태그를 가진 캐릭터)
            reference_chars = []

            # 각 태그를 가진 캐릭터 검색
            for tag in tags[:2]:  # 최대 2개 태그로 검색
                result = await db.execute(
                    select(ChatServiceCharacter)
                    .where(ChatServiceCharacter.tags.contains([tag]))
                    .order_by(desc(ChatServiceCharacter.views))
                    .limit(3)
                )
                chars = result.scalars().all()

                for char in chars:
                    reference_chars.append({
                        'name': char.name,
                        'description': char.description,
                        'tags': char.tags
                    })

            # 중복 제거 (이름 기준)
            seen_names = set()
            unique_refs = []
            for ref in reference_chars:
                if ref['name'] not in seen_names:
                    seen_names.add(ref['name'])
                    unique_refs.append(ref)

            # Gemini API 호출 (1개씩 생성)
            samples = await generate_samples(tags, unique_refs[:3], count=1)

            # 태그 정보 추가
            for sample in samples:
                sample['id'] = i + 1
                sample['tags'] = tags
                sample['basedOn'] = [ref['name'] for ref in unique_refs[:2]]

            all_samples.extend(samples)

        logger.info(f"총 {len(all_samples)}개 캐릭터 샘플 생성 완료")

        return CharacterSampleResponse(samples=all_samples)

    except ValueError as e:
        logger.error(f"설정 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"캐릭터 샘플 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="캐릭터 샘플 생성에 실패했습니다")


# Vercel Serverless Function과 동일한 경로 제공 (로컬 개발용)
@router.post("/generate-character", response_model=CharacterSampleResponse)
async def generate_character(
    request: CharacterSampleRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    로컬 개발 환경용 엔드포인트 (Vercel Serverless Function과 동일한 경로)
    """
    return await generate_character_samples(request, db)
