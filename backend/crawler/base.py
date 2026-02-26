"""
베이스 크롤러 클래스

모든 크롤러가 상속받아 사용하는 기본 클래스입니다.
공통 HTTP 요청, 재시도 로직, 에러 처리를 제공합니다.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, TypeVar

import httpx
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseCrawler(ABC):
    """모든 크롤러의 베이스 클래스

    공통 기능:
    - HTTP 요청 (GET/POST)
    - 지수 백오프 재시도
    - User-Agent 랜덤화
    - 요청 딜레이
    - 에러 처리 및 로깅
    """

    # 기본 HTTP 헤더
    DEFAULT_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    def __init__(
        self,
        source_name: str,
        base_url: str,
        delay: float = 1.5,
        max_retries: int = 3,
        timeout: float = 30.0
    ):
        """
        Args:
            source_name: 크롤러 소스 이름 (예: 'zeta', 'babechat')
            base_url: 기본 URL
            delay: 요청 간 딜레이 (초)
            max_retries: 최대 재시도 횟수
            timeout: 요청 타임아웃 (초)
        """
        self.source_name = source_name
        self.base_url = base_url
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.ua = UserAgent()

    def _get_headers(self, extra_headers: Optional[dict] = None) -> dict:
        """HTTP 헤더 생성

        Args:
            extra_headers: 추가 헤더 (기본 헤더에 병합)

        Returns:
            병합된 헤더 딕셔너리
        """
        headers = {
            **self.DEFAULT_HEADERS,
            "User-Agent": self.ua.random,
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    async def _fetch_html(
        self,
        url: str,
        extra_headers: Optional[dict] = None
    ) -> Optional[str]:
        """HTML 페이지 가져오기 (GET 요청)

        Args:
            url: 요청 URL
            extra_headers: 추가 헤더

        Returns:
            HTML 문자열 또는 None (실패 시)
        """
        headers = self._get_headers(extra_headers)

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(
                    follow_redirects=True,
                    timeout=self.timeout
                ) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    await asyncio.sleep(self.delay)
                    return response.text

            except httpx.HTTPStatusError as e:
                logger.error(f"[{self.source_name}] HTTP 오류 {url}: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"[{self.source_name}] 요청 오류 {url}: {e}")
            except Exception as e:
                logger.error(f"[{self.source_name}] 예상치 못한 오류 {url}: {e}")

            if attempt < self.max_retries - 1:
                wait_time = self.delay * (attempt + 1)
                logger.warning(f"[{self.source_name}] 재시도 중... ({attempt + 1}/{self.max_retries}), {wait_time}초 대기")
                await asyncio.sleep(wait_time)

        return None

    async def _fetch_json(
        self,
        url: str,
        params: Optional[dict] = None,
        extra_headers: Optional[dict] = None
    ) -> Optional[dict]:
        """JSON API 호출 (GET 요청)

        Args:
            url: 요청 URL
            params: URL 파라미터
            extra_headers: 추가 헤더

        Returns:
            JSON 딕셔너리 또는 None (실패 시)
        """
        headers = self._get_headers(extra_headers)
        headers["Accept"] = "application/json"

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    await asyncio.sleep(self.delay)
                    return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"[{self.source_name}] HTTP 오류 {url}: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"[{self.source_name}] 요청 오류 {url}: {e}")
            except Exception as e:
                logger.error(f"[{self.source_name}] JSON 파싱 오류 {url}: {e}")

            if attempt < self.max_retries - 1:
                wait_time = self.delay * (attempt + 1)
                logger.warning(f"[{self.source_name}] 재시도 중... ({attempt + 1}/{self.max_retries})")
                await asyncio.sleep(wait_time)

        return None

    async def _post_json(
        self,
        url: str,
        data: Optional[dict] = None,
        json_data: Optional[dict] = None,
        extra_headers: Optional[dict] = None
    ) -> Optional[dict]:
        """JSON API 호출 (POST 요청)

        Args:
            url: 요청 URL
            data: form 데이터
            json_data: JSON 바디
            extra_headers: 추가 헤더

        Returns:
            JSON 딕셔너리 또는 None (실패 시)
        """
        headers = self._get_headers(extra_headers)

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url,
                        data=data,
                        json=json_data,
                        headers=headers
                    )
                    response.raise_for_status()
                    await asyncio.sleep(self.delay)
                    return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"[{self.source_name}] HTTP 오류 {url}: {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"[{self.source_name}] 요청 오류 {url}: {e}")
            except Exception as e:
                logger.error(f"[{self.source_name}] 오류 {url}: {e}")

            if attempt < self.max_retries - 1:
                wait_time = self.delay * (attempt + 1)
                logger.warning(f"[{self.source_name}] 재시도 중... ({attempt + 1}/{self.max_retries})")
                await asyncio.sleep(wait_time)

        return None

    async def _retry_with_backoff(
        self,
        func: Callable[[], T],
        max_retries: Optional[int] = None,
        base_delay: Optional[float] = None
    ) -> Optional[T]:
        """지수 백오프로 재시도

        Args:
            func: 실행할 함수 (코루틴)
            max_retries: 최대 재시도 횟수 (기본값: self.max_retries)
            base_delay: 기본 딜레이 (기본값: self.delay)

        Returns:
            함수 실행 결과 또는 None (실패 시)
        """
        retries = max_retries or self.max_retries
        delay = base_delay or self.delay

        for attempt in range(retries):
            try:
                return await func()
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"[{self.source_name}] 최대 재시도 횟수 초과: {e}")
                    raise

                wait_time = delay * (2 ** attempt)
                logger.warning(f"[{self.source_name}] 재시도 ({attempt + 1}/{retries}), {wait_time}초 대기")
                await asyncio.sleep(wait_time)

        return None

    @staticmethod
    def parse_korean_number(text: str) -> int:
        """한국어 숫자 표현 파싱 (예: "3,884만" -> 38840000)

        Args:
            text: 숫자 문자열

        Returns:
            정수 값
        """
        try:
            text = text.replace(",", "").strip()

            if "만" in text:
                number = float(text.replace("만", ""))
                return int(number * 10000)

            if "천" in text:
                number = float(text.replace("천", ""))
                return int(number * 1000)

            if "억" in text:
                number = float(text.replace("억", ""))
                return int(number * 100000000)

            return int(text)
        except (ValueError, AttributeError):
            return 0

    @abstractmethod
    async def crawl(self, **kwargs) -> List[Any]:
        """크롤링 실행 - 각 크롤러에서 구현

        Returns:
            크롤링 결과 리스트
        """
        pass


class CharacterCrawler(BaseCrawler):
    """캐릭터 챗봇 서비스 크롤러 베이스 클래스

    캐릭터 데이터를 수집하는 크롤러의 공통 기능을 제공합니다.
    """

    @abstractmethod
    async def crawl_rankings(self, limit: int = 30) -> List[Any]:
        """캐릭터 랭킹 크롤링

        Args:
            limit: 수집할 캐릭터 수

        Returns:
            CharacterData 리스트
        """
        pass

    async def crawl(self, limit: int = 30, **kwargs) -> List[Any]:
        """크롤링 실행 (crawl_rankings 호출)"""
        return await self.crawl_rankings(limit=limit, **kwargs)
