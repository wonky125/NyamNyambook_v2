"""URL을 보고 알맞은 스크래퍼를 선택한다."""
from app.scrapers.base import BaseScraper
from app.scrapers.schema_org import SchemaOrgScraper
from app.scrapers.recipe10000 import Recipe10000Scraper
from app.scrapers.naver import NaverScraper
from app.scrapers.generic import GenericScraper
from app.scrapers.youtube import YouTubeScraper
from app.scrapers.tiktok import TikTokScraper


def get_scraper(url: str) -> BaseScraper:
    if "10000recipe.com" in url:
        return Recipe10000Scraper(url)
    if "blog.naver.com" in url or "post.naver.com" in url:
        return NaverScraper(url)
    if "youtube.com" in url or "youtu.be" in url:
        return YouTubeScraper(url)
    if "tiktok.com" in url or "vm.tiktok.com" in url:
        return TikTokScraper(url)
    # 기본값: recipe-scrapers → SchemaOrg → Generic 폴백 (scrape_service에서 처리)
    return SchemaOrgScraper(url)
