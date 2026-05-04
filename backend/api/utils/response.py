"""
API 표준 응답 유틸리티

모든 API에서 일관된 응답 형식을 사용하기 위한 헬퍼 함수들입니다.
"""
from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """표준 API 응답 모델"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


def success_response(
    data: Any = None,
    message: str = "Success"
) -> dict:
    """성공 응답 생성

    Args:
        data: 응답 데이터
        message: 성공 메시지

    Returns:
        응답 딕셔너리
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(
    error: str,
    message: str = "Error"
) -> dict:
    """에러 응답 생성

    Args:
        error: 에러 상세 정보
        message: 에러 메시지

    Returns:
        응답 딕셔너리
    """
    return {
        "success": False,
        "message": message,
        "error": error
    }
