"""
날짜 관련 유틸리티

API에서 자주 사용하는 날짜 계산 및 필터링 함수들입니다.
"""
from datetime import datetime, timedelta
from typing import Tuple, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import Select

# 타임존 상수
KST = ZoneInfo("Asia/Seoul")
UTC = ZoneInfo("UTC")


def get_kst_today_boundaries_utc() -> Tuple[datetime, datetime]:
    """KST 기준 오늘의 시작/끝을 UTC naive datetime으로 반환

    DB가 UTC naive datetime으로 저장된 경우 사용합니다.

    Returns:
        (UTC 시작 시간, UTC 끝 시간) 튜플 (naive datetime)
    """
    now_kst = datetime.now(KST)
    start_of_day_kst = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day_kst = start_of_day_kst + timedelta(days=1)

    # KST → UTC 변환 후 naive datetime으로
    start_utc = start_of_day_kst.astimezone(UTC).replace(tzinfo=None)
    end_utc = end_of_day_kst.astimezone(UTC).replace(tzinfo=None)

    return start_utc, end_utc


def get_kst_date_boundaries_utc(date: datetime) -> Tuple[datetime, datetime]:
    """특정 날짜의 KST 시작/끝을 UTC naive datetime으로 반환

    Args:
        date: 대상 날짜 (KST 기준으로 해석)

    Returns:
        (UTC 시작 시간, UTC 끝 시간) 튜플 (naive datetime)
    """
    # 입력 날짜를 KST 날짜로 해석
    if date.tzinfo is None:
        date = date.replace(tzinfo=KST)

    start_of_day_kst = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=KST)
    end_of_day_kst = start_of_day_kst + timedelta(days=1)

    # KST → UTC 변환 후 naive datetime으로
    start_utc = start_of_day_kst.astimezone(UTC).replace(tzinfo=None)
    end_utc = end_of_day_kst.astimezone(UTC).replace(tzinfo=None)

    return start_utc, end_utc


def get_day_boundaries(date: datetime) -> Tuple[datetime, datetime]:
    """주어진 날짜의 시작과 끝 시간 반환

    Args:
        date: 대상 날짜

    Returns:
        (시작 시간, 끝 시간) 튜플
    """
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    return start_of_day, end_of_day


def get_date_range(days: int) -> datetime:
    """현재 시간에서 N일 전 시간 반환

    Args:
        days: 이전 일수

    Returns:
        N일 전 datetime
    """
    return datetime.now() - timedelta(days=days)


def parse_date_string(date_str: str, format: str = "%Y-%m-%d") -> Optional[datetime]:
    """날짜 문자열 파싱

    Args:
        date_str: 날짜 문자열
        format: 날짜 형식 (기본: YYYY-MM-DD)

    Returns:
        datetime 객체 또는 None (파싱 실패 시)
    """
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        return None


def filter_by_date_range(
    query: Select,
    column,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    days: Optional[int] = None
) -> Select:
    """쿼리에 날짜 범위 필터 적용

    Args:
        query: SQLAlchemy Select 쿼리
        column: 필터링할 날짜 컬럼
        start_date: 시작 날짜 (선택)
        end_date: 종료 날짜 (선택)
        days: 최근 N일 (start_date/end_date 미지정 시 사용)

    Returns:
        필터가 적용된 쿼리
    """
    if start_date is None and end_date is None and days:
        # 최근 N일 필터
        cutoff = datetime.now() - timedelta(days=days)
        return query.where(column >= cutoff)

    if start_date:
        query = query.where(column >= start_date)
    if end_date:
        query = query.where(column <= end_date)

    return query
