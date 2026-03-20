"""만개의레시피 (10000recipe.com) 전용 스크래퍼"""
import re

from bs4 import BeautifulSoup

from app.schemas.scrape import ScrapedIngredient, ScrapedStep, ScrapeResult
from app.scrapers.base import BaseScraper
from app.utils.text_splitter import normalize_string


class Recipe10000Scraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        html = await self._fetch_html()
        soup = BeautifulSoup(html, "lxml")

        # 제목 — <div class="view2_summary ..."><h3>제목</h3>
        summary_el = soup.select_one(".view2_summary")
        title_el = summary_el.select_one("h3") if summary_el else None
        # 추가 폴백
        if not title_el:
            title_el = soup.select_one(".cont_title h3") or soup.select_one("h1.recipe_title")
        title = normalize_string(title_el.get_text()) if title_el else None

        # 설명 — <div class="view2_summary_in" id="recipeIntro">
        desc_el = soup.select_one("#recipeIntro") or soup.select_one(".view2_summary_in")
        description = normalize_string(desc_el.get_text()) if desc_el else None
        description = description or None

        # 인분 — <span class="view2_summary_info1">2인분</span>
        servings_el = soup.select_one(".view2_summary_info1")
        servings = normalize_string(servings_el.get_text()) if servings_el else None

        # 조리 시간 — <span class="view2_summary_info2">30분 이내</span>
        time_el = soup.select_one(".view2_summary_info2")
        total_time = None
        if time_el:
            m = re.search(r"(\d+)", time_el.get_text())
            if m:
                total_time = int(m.group(1))

        # 이미지 — <img id="main_thumbs"> 또는 .centeredcrop img
        img_el = (
            soup.select_one("#main_thumbs")
            or soup.select_one(".centeredcrop img")
            or soup.select_one(".view2_pic img")
        )
        image_url = None
        if img_el:
            src = img_el.get("src", "")
            # 아이콘·배너 제외
            if src and not any(bad in src for bad in ["cart", "icon", "btn", "banner"]):
                image_url = src if src.startswith("http") else None

        # 재료 — <li> 안에 .ingre_list_name + .ingre_list_ea 가 형제
        ingredients: list[ScrapedIngredient] = []
        for li in soup.select("#divConfirmedMaterialArea ul li, .ready_ingre3 ul li"):
            name_el = li.select_one(".ingre_list_name")
            qty_el = li.select_one(".ingre_list_ea")
            if not name_el:
                continue
            name = normalize_string(name_el.get_text())
            qty_text = normalize_string(qty_el.get_text()) if qty_el else ""
            # "구매" 텍스트 제거
            qty_text = re.sub(r"구매\s*$", "", qty_text).strip()
            m = re.match(r"([\d./]+)?\s*(.+)?", qty_text)
            amount = m.group(1) if m and m.group(1) else None
            unit = m.group(2).strip() if m and m.group(2) else None
            if name:
                ingredients.append(ScrapedIngredient(name=name, amount=amount, unit=unit))

        # 조리 단계 — .view_step .media-body (id="stepdescr1" 등)
        steps: list[ScrapedStep] = []
        step_num = 0
        for body_el in soup.select(".view_step .media-body"):
            text = normalize_string(body_el.get_text())
            if not text:
                continue
            step_num += 1
            # 형제 이미지 div (#stepimgN)
            step_div = body_el.find_parent("div", class_="view_step_cont")
            img_el = step_div.select_one("img") if step_div else None
            img_url = img_el.get("src") if img_el else None
            steps.append(ScrapedStep(step_number=step_num, instruction=text, image_url=img_url))

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
