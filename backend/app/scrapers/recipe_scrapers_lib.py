"""recipe-scrapers 라이브러리 기반 스크래퍼 — 500개 이상 사이트 지원"""
import logging

from recipe_scrapers import scrape_html

from app.schemas.scrape import ScrapedIngredient, ScrapedStep, ScrapeResult
from app.scrapers.base import BaseScraper
from app.utils.text_splitter import normalize_string, parse_ingredient_line

logger = logging.getLogger(__name__)


class RecipeScrapersScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        html = await self._fetch_html()

        # wild_mode=True → 지원 사이트 + Schema.org 방식으로 미지원 사이트도 시도
        scraper = scrape_html(html, org_url=self.url, wild_mode=True)

        title = _safe(scraper.title)
        description = _safe(scraper.description)
        image_url = _safe(scraper.image)
        total_time = _safe(scraper.total_time)   # 분 단위 int
        servings = _safe(lambda: str(scraper.yields())) if _safe(scraper.yields) else None

        # 재료
        raw_ingredients = _safe(scraper.ingredients) or []
        ingredients: list[ScrapedIngredient] = []
        for raw in raw_ingredients:
            parsed = parse_ingredient_line(normalize_string(raw))
            ingredients.append(ScrapedIngredient(**parsed))

        # 조리 단계
        raw_steps = _safe(scraper.instructions_list) or []
        steps: list[ScrapedStep] = []
        for i, text in enumerate(raw_steps, 1):
            text = normalize_string(text)
            if text:
                steps.append(ScrapedStep(step_number=i, instruction=text))

        success = bool(title and (ingredients or steps))

        return ScrapeResult(
            title=normalize_string(title) or None,
            description=normalize_string(description) if description else None,
            servings=servings,
            total_time=total_time if isinstance(total_time, int) and total_time > 0 else None,
            image_url=image_url or None,
            source_url=self.url,
            source_type="web",
            steps=steps,
            ingredients=ingredients,
            scrape_success=success,
        )


def _safe(fn):
    """예외를 삼키고 None 반환 — 필드 하나 실패가 전체를 죽이지 않도록."""
    try:
        return fn()
    except Exception:
        return None
