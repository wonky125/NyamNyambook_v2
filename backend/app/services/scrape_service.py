"""스크래핑 + 자동 태그 추천"""
import logging

from app.scrapers import get_scraper
from app.scrapers.generic import GenericScraper
from app.scrapers.recipe_scrapers_lib import RecipeScrapersScraper
from app.scrapers.schema_org import SchemaOrgScraper
from app.schemas.scrape import ScrapeResult
from app.utils.auto_tagger import suggest_tags

logger = logging.getLogger(__name__)


async def scrape_url(url: str) -> ScrapeResult:
    """
    URL을 스크래핑한다.
    - 실패하면 scrape_success=False인 결과 반환 (앱 오류 아님)
    - 자동 태그 제안 포함

    폴백 순서 (전용 스크래퍼가 없는 일반 URL):
      1. recipe-scrapers (500개+ 사이트 + wild_mode Schema.org)
      2. SchemaOrgScraper (extruct 기반)
      3. GenericScraper (제목/이미지만)
    """
    scraper = get_scraper(url)
    is_generic = isinstance(scraper, SchemaOrgScraper)

    if is_generic:
        # 일반 URL: recipe-scrapers 먼저 시도
        result = await _try_scrape(RecipeScrapersScraper(url), url)
        if not result.scrape_success:
            logger.info("recipe-scrapers 실패, SchemaOrg 시도: %s", url)
            result = await _try_scrape(SchemaOrgScraper(url), url)
        if not result.scrape_success:
            logger.info("SchemaOrg 실패, Generic 시도: %s", url)
            result = await _try_scrape(GenericScraper(url), url)
    else:
        # 10000recipe, naver 등 전용 스크래퍼
        result = await _try_scrape(scraper, url)

    # 자동 태그 추천
    ingredient_names = [ing.name for ing in result.ingredients]
    result.suggested_tags = suggest_tags(result.title or "", ingredient_names)

    return result


async def _try_scrape(scraper, url: str) -> ScrapeResult:
    try:
        return await scraper.scrape()
    except Exception as exc:
        logger.warning("Scraper %s failed for %s: %s", type(scraper).__name__, url, exc)
        return ScrapeResult(source_url=url, scrape_success=False)
