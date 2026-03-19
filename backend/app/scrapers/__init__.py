"""URL을 보고 알맞은 스크래퍼를 선택한다."""
from app.scrapers.base import BaseScraper
from app.scrapers.schema_org import SchemaOrgScraper
from app.scrapers.recipe10000 import Recipe10000Scraper
from app.scrapers.naver import NaverScraper
from app.scrapers.generic import GenericScraper


def get_scraper(url: str) -> BaseScraper:
    if "10000recipe.com" in url:
        return Recipe10000Scraper(url)
    if "blog.naver.com" in url or "post.naver.com" in url:
        return NaverScraper(url)
    # 기본값: Schema.org 먼저 시도, 실패하면 generic으로 폴백
    return SchemaOrgScraper(url)
