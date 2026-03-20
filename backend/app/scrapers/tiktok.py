"""TikTok 레시피 스크래퍼
전략: __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON 파싱 (YouTube ytInitialData와 동일한 방식)
참고: Q-Bukold/TikTok-Content-Scraper, HasData/tiktok-scraping

성공률:
  - Vercel (서버 IP): 30~50% (쿠키 없음)
  - Railway + 프록시: 90%+ (나중에 추가 예정)
  - 실패 시: scrape_success=False → 수동 입력 폼 폴백 (CLAUDE.md 정책)
"""
import json
import logging
import re

import httpx
from bs4 import BeautifulSoup

from app.schemas.scrape import ScrapedIngredient, ScrapedStep, ScrapeResult
from app.scrapers.base import BaseScraper
from app.utils.text_splitter import normalize_string, parse_ingredient_line, split_youtube_description

logger = logging.getLogger(__name__)

# TikTok은 브라우저에 최대한 가까운 헤더가 필요
_TIKTOK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Referer": "https://www.tiktok.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}


def _extract_item_struct(html: str) -> dict | None:
    """HTML에서 __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON을 파싱해 itemStruct 반환"""
    soup = BeautifulSoup(html, "lxml")
    script = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")
    if not script or not script.string:
        return None

    try:
        data = json.loads(script.string)
        detail = (
            data.get("__DEFAULT_SCOPE__", {})
            .get("webapp.video-detail", {})
        )
        # statusCode 0 = 성공, 그 외 = 에러(영상 없음, 비공개, 지역 차단 등)
        status = detail.get("statusCode", 0)
        if status != 0:
            logger.warning("[TikTok] statusCode=%s (%s)", status, detail.get("statusMsg", ""))
            return None
        return detail.get("itemInfo", {}).get("itemStruct")
    except (json.JSONDecodeError, AttributeError):
        return None


def _get_thumbnail(item: dict, url: str) -> str | None:
    """썸네일 URL 추출"""
    video = item.get("video", {})
    for key in ("originCover", "cover", "dynamicCover"):
        val = video.get(key)
        if val:
            return val
    return None


class TikTokScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        # HTTP/2 + 세션 쿠키 유지 (봇 감지 우회)
        try:
            async with httpx.AsyncClient(
                headers=_TIKTOK_HEADERS,
                timeout=8,
                follow_redirects=True,
                http2=True,
            ) as client:
                response = await client.get(self.url)
                response.raise_for_status()
                html = response.text
        except Exception as exc:
            logger.warning("[TikTok] HTTP 요청 실패: %s", exc)
            return ScrapeResult(source_url=self.url, scrape_success=False)

        item = _extract_item_struct(html)
        if not item:
            logger.warning("[TikTok] __UNIVERSAL_DATA_FOR_REHYDRATION__ 없음 (봇 차단 가능성): %s", self.url)
            return ScrapeResult(source_url=self.url, scrape_success=False)

        # 캡션 (= desc 필드)
        caption = item.get("desc", "")
        if not caption:
            logger.warning("[TikTok] 캡션이 비어 있음: %s", self.url)
            return ScrapeResult(source_url=self.url, scrape_success=False)

        # 해시태그 제거 후 레시피 텍스트만 파싱
        hashtags = {t.get("hashtagName", "") for t in item.get("textExtra", []) if t.get("hashtagName")}
        clean_caption = _remove_hashtags(caption, hashtags)

        title = normalize_string(caption.split("\n")[0][:100]) or "TikTok 레시피"
        thumbnail = _get_thumbnail(item, self.url)

        # YouTube description 파싱 로직 재사용 (구조 동일)
        ingredients_raw, steps_raw = split_youtube_description(clean_caption)

        ingredients = [
            ScrapedIngredient(**parse_ingredient_line(normalize_string(r)))
            for r in ingredients_raw
        ]
        steps = [
            ScrapedStep(step_number=i, instruction=normalize_string(s))
            for i, s in enumerate(steps_raw, 1)
            if normalize_string(s)
        ]

        success = bool(ingredients or steps)
        logger.info(
            "[TikTok] %s — 재료:%d 단계:%d",
            "성공" if success else "재료/단계 없음",
            len(ingredients), len(steps),
        )

        return ScrapeResult(
            title=title,
            image_url=thumbnail,
            source_url=self.url,
            source_type="web",
            ingredients=ingredients,
            steps=steps,
            scrape_success=success,
        )


def _remove_hashtags(text: str, hashtag_names: set[str]) -> str:
    """캡션에서 해시태그(#tag) 제거"""
    cleaned = re.sub(r"#\w+", "", text)
    return re.sub(r"\s+", " ", cleaned).strip()
