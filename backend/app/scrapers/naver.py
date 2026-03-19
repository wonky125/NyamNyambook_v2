"""네이버 블로그 / 포스트 스크래퍼 — 구조가 없으면 폴백"""
import re

from bs4 import BeautifulSoup

from app.schemas.scrape import ScrapedIngredient, ScrapedStep, ScrapeResult
from app.scrapers.base import BaseScraper, HEADERS
from app.utils.text_splitter import normalize_string
import httpx


class NaverScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        # 네이버 블로그는 iframe 내부에 실제 콘텐츠가 있음
        post_url = self._to_post_url(self.url)
        async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            resp = await client.get(post_url)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "lxml")

        # 제목
        title_el = (
            soup.select_one(".se-title-text")       # 스마트에디터 One
            or soup.select_one(".htitle")            # 구 에디터
            or soup.select_one("title")
        )
        title = normalize_string(title_el.get_text()) if title_el else None

        # 본문 텍스트 — 재료/단계를 자동 파싱하기 어려우므로 description에 담기
        body_el = soup.select_one(".se-main-container") or soup.select_one("#postViewArea")
        body_text = normalize_string(body_el.get_text("\n")) if body_el else ""

        # 이미지
        img_el = soup.select_one(".se-image-resource") or soup.select_one(".post-image img")
        image_url = img_el.get("src") if img_el else None

        # 재료/단계 파싱은 구조가 없어 어려움 — 빈 리스트 반환 (폼에서 직접 입력)
        return ScrapeResult(
            title=title,
            description=body_text[:500] if body_text else None,
            image_url=image_url,
            source_url=self.url,
            source_type="naver",
            steps=[],
            ingredients=[],
            scrape_success=bool(title),
        )

    @staticmethod
    def _to_post_url(url: str) -> str:
        """blog.naver.com/ID/POST → blog.naver.com/PostView.naver?blogId=ID&logNo=POST"""
        m = re.match(r"https?://blog\.naver\.com/([^/]+)/(\d+)", url)
        if m:
            return f"https://blog.naver.com/PostView.naver?blogId={m.group(1)}&logNo={m.group(2)}"
        return url
