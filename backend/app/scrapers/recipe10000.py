"""만개의레시피 (10000recipe.com) 전용 스크래퍼"""
import re

import httpx
from bs4 import BeautifulSoup

from app.schemas.scrape import ScrapedIngredient, ScrapedStep, ScrapeResult
from app.scrapers.base import BaseScraper
from app.utils.text_splitter import normalize_string


class Recipe10000Scraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        html = await self._fetch_html()
        soup = BeautifulSoup(html, "lxml")

        # 제목
        title_el = soup.select_one(".view2_summary h3") or soup.select_one(".view_summary h3")
        title = normalize_string(title_el.get_text()) if title_el else None

        # 설명
        desc_el = soup.select_one(".view2_summary_in .view_summary_other") or soup.select_one(".summary_other")
        description = normalize_string(desc_el.get_text()) if desc_el else None

        # 인분 / 시간
        info_els = soup.select(".view2_summary_tbl td") or soup.select(".summary_tbl td")
        servings = None
        total_time = None
        for i, el in enumerate(info_els):
            text = el.get_text(strip=True)
            if "인분" in text:
                servings = text
            m = re.search(r"(\d+)", text)
            if "분" in text and m:
                total_time = int(m.group(1))

        # 이미지
        img_el = soup.select_one(".view_pic img") or soup.select_one(".main_pic img")
        image_url = img_el.get("src") if img_el else None

        # 재료
        ingredients: list[ScrapedIngredient] = []
        for item in soup.select(".ingre_list_name") or soup.select(".ingredient_list li"):
            name_el = item.select_one(".ingre_list_name_item") or item
            qty_el = item.select_one(".ingre_list_ea")
            name = normalize_string(name_el.get_text())
            qty_text = normalize_string(qty_el.get_text()) if qty_el else ""
            # 양과 단위 분리
            m = re.match(r"([\d./]+)?\s*(.+)?", qty_text)
            amount = m.group(1) if m and m.group(1) else None
            unit = m.group(2).strip() if m and m.group(2) else None
            if name:
                ingredients.append(ScrapedIngredient(name=name, amount=amount, unit=unit))

        # 재료 대안 선택자
        if not ingredients:
            for row in soup.select(".ready_ingre3 ul li"):
                text = normalize_string(row.get_text())
                if text:
                    parts = text.rsplit(" ", 1)
                    name = parts[0] if len(parts) > 1 else text
                    qty = parts[1] if len(parts) > 1 else None
                    ingredients.append(ScrapedIngredient(name=name, amount=qty))

        # 조리 단계
        steps: list[ScrapedStep] = []
        for i, step_el in enumerate(soup.select(".step_list .step_list_text") or soup.select(".step li"), 1):
            text = normalize_string(step_el.get_text())
            img_el = step_el.find_previous_sibling("img") or step_el.select_one("img")
            img_url = img_el.get("src") if img_el else None
            if text:
                steps.append(ScrapedStep(step_number=i, instruction=text, image_url=img_url))

        return ScrapeResult(
            title=title,
            description=description,
            servings=servings,
            total_time=total_time,
            image_url=image_url,
            source_url=self.url,
            source_type="web",
            steps=steps,
            ingredients=ingredients,
            scrape_success=bool(title),
        )
