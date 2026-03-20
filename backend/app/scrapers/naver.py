"""네이버 블로그 / 포스트 스크래퍼"""
import re

from bs4 import BeautifulSoup

from app.schemas.scrape import ScrapedIngredient, ScrapedStep, ScrapeResult
from app.scrapers.base import BaseScraper, HEADERS
from app.utils.text_splitter import normalize_string
import httpx


# 재료 패턴: "소고기 200g", "양파 1개" 등
_ING_PATTERN = re.compile(
    r"[가-힣a-zA-Z]+.*\d+|[가-힣a-zA-Z]+.*(?:큰술|작은술|컵|개|마리|g|kg|ml|L|꼬집|주먹|T|t|스푼|알|장|줌)",
)
_STEP_START = re.compile(r"^(\d+[.\)]\s*|step\s*\d+)", re.IGNORECASE)
_ING_HEADER = re.compile(r"ingredient|재료|양념|sauce|준비물", re.IGNORECASE)
_STEP_HEADER = re.compile(r"step|direction|instruction|만드|조리|how.*make|cook", re.IGNORECASE)
_GARBAGE = [
    "http", "www", ".com", "구독", "좋아요", "instagram",
    "문의", "협찬", "광고", "비즈니스", "출처",
]


def _split_blog_text(full_text: str) -> tuple[list[str], list[str]]:
    """비구조적 블로그 본문에서 재료/조리순서를 추출한다 (Flask 원본 로직 포팅)."""
    if not full_text:
        return [], []

    lines = full_text.split("\n")
    ingredients: list[str] = []
    steps: list[str] = []
    mode = 0  # 0=미분류, 1=재료, 2=단계
    last_was_ing = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        lower = line.lower()

        # 광고·SNS 라인 제거
        if any(bad in lower for bad in _GARBAGE):
            continue
        # 타임스탬프 제거 (0:00 -)
        if re.match(r"^\d{1,2}:\d{2}\s*[-–—]", line):
            continue

        # 섹션 헤더 감지
        if ":" in line and _ING_HEADER.search(line):
            mode = 1
            last_was_ing = True
            continue
        if ":" in line and _STEP_HEADER.search(line):
            mode = 2
            last_was_ing = False
            continue

        if mode == 1:
            if len(line) < 120 and not _STEP_START.match(line):
                clean = re.sub(r"^[►▪•\-\*\s]+", "", line)
                if clean and len(clean) > 3 and clean not in ingredients:
                    ingredients.append(clean)
            elif _STEP_START.match(line):
                mode = 2
                last_was_ing = False
                steps.append(line)
        elif mode == 2:
            steps.append(line)
        else:
            if _STEP_START.match(line):
                steps.append(line)
                mode = 2
                last_was_ing = False
            elif len(line) < 80 and _ING_PATTERN.search(line):
                clean = re.sub(r"^[►▪•\-\*\s]+", "", line)
                if clean and len(clean) > 3:
                    ingredients.append(clean)
                    last_was_ing = True
            elif last_was_ing and len(line) < 120 and not _STEP_START.match(line):
                clean = re.sub(r"^[►▪•\-\*\s]+", "", line)
                if clean and len(clean) > 3:
                    ingredients.append(clean)
            elif len(line) > 20:
                steps.append(line)
                last_was_ing = False

    return ingredients, steps


class NaverScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        # 네이버 블로그는 iframe 내부에 실제 콘텐츠 — PostView URL로 직접 접근
        post_url = self._to_post_url(self.url)

        async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            resp = await client.get(post_url)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "lxml")

        # 제목 (다중 셀렉터 — 스마트에디터 One / 구 에디터 / og:title)
        title = None
        for selector in [
            ".se-title-text", ".se_textarea", ".htitle",
            "h3.tit_h3", ".pcol1", ".post_title", "#title_1",
        ]:
            el = soup.select_one(selector)
            if el:
                title = normalize_string(el.get_text())
                break
        if not title:
            og = soup.select_one('meta[property="og:title"]')
            title = og.get("content", "").strip() if og else None

        # 본문 영역
        body_el = (
            soup.select_one(".se-main-container")
            or soup.select_one("#postViewArea")
            or soup.select_one(".se_component_wrap")
            or soup.select_one(".post_ct")
        )
        body_text = body_el.get_text("\n", strip=True) if body_el else soup.get_text("\n", strip=True)

        # 이미지
        image_url = None
        for selector in [
            ".se-image-resource", ".se_mediaImage img",
            "#postViewArea img", ".post-image img",
        ]:
            img_el = soup.select_one(selector)
            if img_el:
                src = img_el.get("data-lazy-src") or img_el.get("src", "")
                if src and src.startswith("http"):
                    image_url = src
                    break
        if not image_url:
            og_img = soup.select_one('meta[property="og:image"]')
            if og_img:
                image_url = og_img.get("content", "") or None

        # 재료·단계 — 본문 텍스트 파싱
        raw_ingredients, raw_steps = _split_blog_text(body_text)

        ingredients = [
            ScrapedIngredient(name=line) for line in raw_ingredients if line
        ]
        steps = [
            ScrapedStep(step_number=i + 1, instruction=line)
            for i, line in enumerate(raw_steps) if line
        ]

        return ScrapeResult(
            title=title,
            description=body_text[:400] if body_text else None,
            image_url=image_url,
            source_url=self.url,
            source_type="naver",
            steps=steps,
            ingredients=ingredients,
            scrape_success=bool(title),
        )

    @staticmethod
    def _to_post_url(url: str) -> str:
        """blog.naver.com/ID/POST → PostView URL (iframe 없이 직접 접근)"""
        m = re.match(r"https?://blog\.naver\.com/([^/]+)/(\d+)", url)
        if m:
            return f"https://blog.naver.com/PostView.naver?blogId={m.group(1)}&logNo={m.group(2)}"
        return url
