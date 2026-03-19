"""스크래퍼 추상 기반 클래스"""
from abc import ABC, abstractmethod

import httpx

from app.schemas.scrape import ScrapeResult

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
}


class BaseScraper(ABC):
    """모든 스크래퍼의 공통 인터페이스"""

    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    async def scrape(self) -> ScrapeResult:
        """URL을 스크래핑해서 ScrapeResult를 반환한다."""
        ...

    async def _fetch_html(self) -> str:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            response = await client.get(self.url)
            response.raise_for_status()
            return response.text
