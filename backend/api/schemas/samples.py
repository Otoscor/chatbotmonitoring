"""캐릭터 샘플 생성 관련 스키마"""
from typing import List
from pydantic import BaseModel


class CharacterSampleRequest(BaseModel):
    """캐릭터 샘플 생성 요청"""
    tag_combinations: List[List[str]]  # 예: [["판타지", "아카데미"], ["액션", "학교"]]


class CharacterSampleResponse(BaseModel):
    """캐릭터 샘플 응답"""
    samples: List[dict]  # 생성된 캐릭터 샘플 리스트
