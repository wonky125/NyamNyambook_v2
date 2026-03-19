"""스크래핑 + 자동 태그 추천"""
import logging

from app.scrapers import get_scraper
from app.scrapers.generic import GenericScraper
from app.schemas.scrape import ScrapeResult
from app.utils.auto_tagger import suggest_tags

logger = logging.getLogger(__name__)


async def scrape_url(url: str) -> ScrapeResult:
    """
    URL을 스크래핑한다.
    - 실패하면 scrape_success=False인 결과 반환 (앱 오류 아님)
    - 자동 태그 제안 포함
    """
    scraper = get_scraper(url)
    try:
        result = await scraper.scrape()
    except Exception as exc:
        logger.warning("Scrape failed for %s: %s", url, exc)
        # Schema.org 스크래퍼가 실패하면 generic으로 재시도
        try:
            result = await GenericScraper(url).scrape()
        except Exception as exc2:
            logger.warning("Generic scrape also failed: %s", exc2)
            result = ScrapeResult(source_url=url, scrape_success=False)

    # 자동 태그 추천
    ingredient_names = [ing.name for ing in result.ingredients]
    result.suggested_tags = suggest_tags(result.title or "", ingredient_names)

    return result
