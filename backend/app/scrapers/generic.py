"""Schema.org 없는 페이지용 최선-노력(best-effort) 스크래퍼"""
from bs4 import BeautifulSoup

from app.schemas.scrape import ScrapeResult
from app.scrapers.base import BaseScraper
from app.utils.text_splitter import normalize_string


class GenericScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        html = await self._fetch_html()
        soup = BeautifulSoup(html, "lxml")

        title_el = soup.find("h1") or soup.find("title")
        title = normalize_string(title_el.get_text()) if title_el else None

        img_el = soup.select_one("article img") or soup.select_one("main img") or soup.find("img")
        image_url = img_el.get("src") if img_el else None

        return ScrapeResult(
            title=title,
            image_url=image_url,
            source_url=self.url,
            source_type="web",
            scrape_success=bool(title),
        )
