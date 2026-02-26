"""
Gemini API 클라이언트
캐릭터 샘플 생성에 사용
"""
import httpx
import json
import logging
from typing import List, Dict
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


async def generate_character_samples(
    tags: List[str],
    reference_characters: List[Dict],
    count: int = 3
) -> List[Dict]:
    """
    Gemini API를 사용하여 캐릭터 샘플 생성

    Args:
        tags: 태그 조합 리스트
        reference_characters: 참고할 인기 캐릭터 정보
        count: 생성할 샘플 수

    Returns:
        생성된 캐릭터 샘플 리스트
    """
    if not settings.gemini_api_key:
        raise ValueError("Gemini API 키가 설정되지 않았습니다. GEMINI_API_KEY 환경 변수를 설정하세요.")

    # 프롬프트 생성
    prompt = create_prompt(tags, reference_characters, count)

    # API 요청 (타임아웃 증가)
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{GEMINI_API_URL}?key={settings.gemini_api_key}",
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.8,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 16384,
                    }
                },
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()
            result = response.json()

            # 응답 파싱
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
            samples = parse_generated_samples(generated_text, count)

            logger.info(f"Gemini API로 {len(samples)}개 캐릭터 샘플 생성 완료")
            return samples

        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API 오류: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"캐릭터 샘플 생성 중 오류: {str(e)}")
            raise


def create_prompt(tags: List[str], reference_characters: List[Dict], count: int) -> str:
    """프롬프트 생성"""

    # 참고 캐릭터 정보 요약
    ref_info = ""
    for i, char in enumerate(reference_characters[:3], 1):
        ref_info += f"\n{i}. {char.get('name', '')}"
        if char.get('description'):
            ref_info += f"\n   설명: {char['description'][:200]}..."
        if char.get('tags'):
            ref_info += f"\n   태그: {', '.join(char['tags'][:5])}"

    prompt = f"""당신은 AI 캐릭터 챗봇 전문 크리에이터입니다.
현재 인기 있는 캐릭터들을 분석하여 새로운 캐릭터 제작 가이드를 만들어주세요.

## 주어진 태그 조합
{', '.join(tags)}

## 참고할 인기 캐릭터
{ref_info}

## 요청사항
위 태그 조합을 기반으로 {count}개의 독창적인 캐릭터 제작 가이드를 생성해주세요.
각 캐릭터마다 다음 정보를 포함해야 합니다:

1. **작품 제목 (title)**: 이 캐릭터 작품의 매력적인 제목 (예: "달빛 아래의 기사", "금지된 계약")
2. **작품 소개글 (description)**: 작품 전체를 소개하는 매력적인 문구 (100자 이상)
3. **캐릭터명 (name)**: 태그와 어울리는 매력적인 이름
4. **캐릭터 프로필 (profile)**: 외모, 성격, 말투를 포함한 상세 프로필 (200자 이상)
5. **배경 소개글 (backgroundIntro)**: 세계관 배경 간단 소개 (50자 이상)
6. **세계관 프롬프트 (worldPrompt)**: AI에게 전달할 세계관 시스템 프롬프트 (150자 이상, 구체적인 설정 포함)
7. **첫날 상황 (firstDaySituation)**: 유저와 캐릭터가 처음 만나는 상황 설명 (100자 이상)
8. **시작 메시지 (openingMessage)**: 캐릭터가 유저에게 보내는 첫 대사 (캐릭터의 말투와 성격이 드러나도록)
9. **대표 장르 (genre)**: 로맨스, 판타지, 드라마, 무협, 공포, 스포츠, 기타 중 택1
10. **해시태그 (hashtags)**: 검색용 해시태그 5개 (배열 형태)

## 응답 형식 (JSON)
```json
[
  {{
    "title": "작품 제목",
    "description": "작품 소개글",
    "name": "캐릭터 이름",
    "profile": "외모, 성격, 말투를 포함한 상세 프로필",
    "backgroundIntro": "세계관 배경 소개",
    "worldPrompt": "AI 시스템 프롬프트용 세계관 설정",
    "firstDaySituation": "첫 만남 상황 설명",
    "openingMessage": "캐릭터의 첫 대사",
    "genre": "로맨스",
    "hashtags": ["태그1", "태그2", "태그3", "태그4", "태그5"]
  }}
]
```

**중요**: 반드시 JSON 형식으로만 응답하세요. 추가 설명은 필요 없습니다."""

    return prompt


def parse_generated_samples(text: str, expected_count: int) -> List[Dict]:
    """생성된 텍스트에서 JSON 파싱"""
    try:
        # JSON 추출 (마크다운 코드 블록 제거)
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        text = text.strip()

        # JSON 파싱
        samples = json.loads(text)

        # 검증
        if not isinstance(samples, list):
            raise ValueError("응답이 리스트 형식이 아닙니다")

        # 필수 필드 확인
        required_fields = [
            "title", "description", "name", "profile", "backgroundIntro",
            "worldPrompt", "firstDaySituation", "openingMessage", "genre", "hashtags"
        ]
        for sample in samples:
            for field in required_fields:
                if field not in sample:
                    if field == "hashtags":
                        sample[field] = []
                    else:
                        sample[field] = "정보 없음"

        return samples[:expected_count]

    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류: {str(e)}\n응답 텍스트: {text}")
        # 폴백: 빈 샘플 반환
        return [{
            "title": f"샘플 {i+1}",
            "description": "Gemini API 응답 파싱에 실패했습니다.",
            "name": f"캐릭터 {i+1}",
            "profile": "생성 실패",
            "backgroundIntro": "생성 실패",
            "worldPrompt": "생성 실패",
            "firstDaySituation": "생성 실패",
            "openingMessage": "생성 실패",
            "genre": "기타",
            "hashtags": []
        } for i in range(expected_count)]
