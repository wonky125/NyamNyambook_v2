"""Schema.org Recipe JSON-LD 파서 — 범용 웹사이트 지원"""
import json
import re

import extruct
from bs4 import BeautifulSoup

from app.schemas.scrape import ScrapedIngredient, ScrapedStep, ScrapeResult
from app.scrapers.base import BaseScraper
from app.utils.text_splitter import normalize_string, parse_ingredient_line


def _parse_duration_to_minutes(value: str | None) -> int | None:
    """ISO 8601 (PT30M) 또는 '30분' 텍스트 → 정수 분"""
    if not value:
        return None
    # ISO 8601
    match = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?", value, re.IGNORECASE)
    if match:
        days, hours, minutes = (int(x or 0) for x in match.groups())
        total = days * 24 * 60 + hours * 60 + minutes
        return total or None
    # 한국어 숫자 (30분, 1시간 30분)
    hours_m = re.search(r"(\d+)\s*시간", value)
    mins_m = re.search(r"(\d+)\s*분", value)
    total = int(hours_m.group(1)) * 60 if hours_m else 0
    total += int(mins_m.group(1)) if mins_m else 0
    return total or None


def _extract_schema_recipe(data: dict) -> dict | None:
    """extruct 결과에서 Recipe 타입 찾기"""
    for item in data.get("json-ld", []):
        if isinstance(item, dict):
            types = item.get("@type", [])
            if isinstance(types, str):
                types = [types]
            if "Recipe" in types:
                return item
    return None


def _to_str_list(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    return []


class SchemaOrgScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        html = await self._fetch_html()
        soup = BeautifulSoup(html, "lxml")

        structured = extruct.extract(html, base_url=self.url, syntaxes=["json-ld"])
        recipe = _extract_schema_recipe(structured)

        if not recipe:
            return ScrapeResult(source_url=self.url, scrape_success=False)

        # 제목
        title = normalize_string(recipe.get("name", ""))

        # 설명
        description = normalize_string(recipe.get("description", "")) or None

        # 시간
        prep_time = _parse_duration_to_minutes(recipe.get("prepTime"))
        cook_time = _parse_duration_to_minutes(recipe.get("cookTime"))
        total_time = _parse_duration_to_minutes(recipe.get("totalTime"))

        # 인분
        servings = recipe.get("recipeYield")
        if isinstance(servings, list):
            servings = servings[0] if servings else None
        servings = str(servings) if servings else None

        # 이미지
        image = recipe.get("image")
        if isinstance(image, list):
            image = image[0]
        if isinstance(image, dict):
            image = image.get("url")
        image_url = str(image) if image else None

        # 재료
        raw_ingredients = _to_str_list(recipe.get("recipeIngredient", []))
        ingredients: list[ScrapedIngredient] = []
        for raw in raw_ingredients:
            parsed = parse_ingredient_line(normalize_string(raw))
            ingredients.append(ScrapedIngredient(**parsed))

        # 조리 단계
        raw_steps = recipe.get("recipeInstructions", [])
        if isinstance(raw_steps, str):
            raw_steps = [raw_steps]
        steps: list[ScrapedStep] = []
        for i, step in enumerate(raw_steps, 1):
            if isinstance(step, dict):
                text = step.get("text", "")
                img = step.get("image")
                if isinstance(img, list):
                    img = img[0] if img else None
                if isinstance(img, dict):
                    img = img.get("url")
            else:
                text = str(step)
                img = None
            text = normalize_string(text)
            if text:
                steps.append(ScrapedStep(step_number=i, instruction=text, image_url=img))

        return ScrapeResult(
            title=title or None,
            description=description,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            total_time=total_time,
            image_url=image_url,
            source_url=self.url,
            source_type="web",
            steps=steps,
            ingredients=ingredients,
            scrape_success=bool(title),
        )
