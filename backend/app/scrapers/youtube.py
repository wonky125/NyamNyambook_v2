"""YouTube 레시피 스크래퍼
파싱 전략:
  1. ytInitialData 추출 (빠름, API 키 불필요) — 기존 코드 이식
  2. youtube-transcript-api 폴백 (설명에 재료 없을 때)
"""
import json
import logging
import re

from bs4 import BeautifulSoup

from app.schemas.scrape import ScrapedIngredient, ScrapedStep, ScrapeResult
from app.scrapers.base import BaseScraper, HEADERS
from app.utils.text_splitter import normalize_string, parse_ingredient_line, split_youtube_description

logger = logging.getLogger(__name__)

_LANG_ATTEMPTS = [
    ("ko-KR,ko;q=0.9,en;q=0.8", "한글"),
    ("en-US,en;q=0.9", "영문"),
]


def _extract_video_id(url: str) -> str:
    """YouTube URL에서 영상 ID 추출"""
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    if "/shorts/" in url:
        return url.split("/shorts/")[-1].split("?")[0]
    return ""


def _get_watch_contents(data: dict) -> list:
    try:
        return (
            data["contents"]["twoColumnWatchNextResults"]
            ["results"]["results"]["contents"]
        )
    except (KeyError, TypeError):
        return []


def _extract_title(data: dict) -> str:
    try:
        for item in _get_watch_contents(data):
            renderer = item.get("videoPrimaryInfoRenderer") or item.get("compositeVideoPrimaryInfoRenderer")
            if renderer:
                return renderer["title"]["runs"][0]["text"]
    except Exception:
        pass
    return ""


def _find_description(data: dict) -> str:
    """ytInitialData에서 영상 설명 추출.
    현재 구조: contents[1]['videoSecondaryInfoRenderer']['attributedDescription']['content']
    폴백: 재귀 탐색
    """
    # 직접 접근 (가장 빠름)
    try:
        for item in _get_watch_contents(data):
            secondary = item.get("videoSecondaryInfoRenderer", {})
            if secondary:
                desc = secondary.get("attributedDescription", {}).get("content", "")
                if desc:
                    return desc
                desc = secondary.get("description", {}).get("simpleText", "")
                if desc:
                    return desc
    except Exception:
        pass

    # 재귀 폴백
    return _find_description_recursive(data)


def _find_description_recursive(obj, max_depth: int = 12, depth: int = 0) -> str:
    if depth >= max_depth:
        return ""
    if isinstance(obj, dict):
        if "attributedDescription" in obj:
            content = obj["attributedDescription"].get("content", "")
            if content and len(content) > 150:
                return content
        if "description" in obj and isinstance(obj["description"], dict):
            text = obj["description"].get("simpleText", "")
            if text and len(text) > 150:
                return text
        for v in obj.values():
            result = _find_description_recursive(v, max_depth, depth + 1)
            if result and len(result) > 150:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _find_description_recursive(item, max_depth, depth + 1)
            if result and len(result) > 150:
                return result
    return ""


class YouTubeScraper(BaseScraper):
    async def scrape(self) -> ScrapeResult:
        vid_id = _extract_video_id(self.url)
        image_url = f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg" if vid_id else None

        # 전략 1: ytInitialData (한글 → 영문 순서로 시도)
        for accept_lang, lang_name in _LANG_ATTEMPTS:
            result = await self._try_yt_initial_data(accept_lang, lang_name, vid_id, image_url)
            if result:
                return result

        # 전략 2: youtube-transcript-api (자막)
        if vid_id:
            result = await self._try_transcript(vid_id, image_url)
            if result:
                return result

        logger.warning("[YouTube] 모든 전략 실패: %s", self.url)
        return ScrapeResult(source_url=self.url, scrape_success=False)

    async def _try_yt_initial_data(
        self, accept_lang: str, lang_name: str, vid_id: str, image_url: str | None
    ) -> ScrapeResult | None:
        try:
            import httpx
            headers = {**HEADERS, "Accept-Language": accept_lang}
            async with httpx.AsyncClient(headers=headers, timeout=8, follow_redirects=True) as client:
                response = await client.get(self.url)
                response.raise_for_status()
                html = response.text

            soup = BeautifulSoup(html, "lxml")
            for script in soup.find_all("script"):
                if not script.string or "ytInitialData" not in script.string:
                    continue
                match = re.search(r"var ytInitialData = ({.*?});", script.string)
                if not match:
                    continue

                data = json.loads(match.group(1))
                title = _extract_title(data) or "YouTube 레시피"
                description = _find_description(data)


                if not description or len(description) < 150:
                    logger.info("[YouTube] %s 설명 부족, 다음 시도", lang_name)
                    return None

                korean_count = sum(1 for c in description if "가" <= c <= "힣")
                has_korean = korean_count > 20

                # 한글 시도인데 한글 없으면 영문 시도로 넘김
                if accept_lang.startswith("ko") and not has_korean:
                    return None

                ingredients_raw, steps_raw = split_youtube_description(description)
                logger.info(
                    "[YouTube] %s 성공 — 재료:%d 단계:%d",
                    lang_name, len(ingredients_raw), len(steps_raw),
                )
                return self._build_result(title, image_url, ingredients_raw, steps_raw)

        except Exception as exc:
            logger.warning("[YouTube] ytInitialData %s 실패: %s", lang_name, exc)
            return None

    async def _try_transcript(self, vid_id: str, image_url: str | None) -> ScrapeResult | None:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            import asyncio
            ytt = YouTubeTranscriptApi()
            transcript = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ytt.fetch(vid_id, languages=["ko", "en"]),
            )
            text = " ".join(snippet.text for snippet in transcript)
            logger.info("[YouTube] 자막 추출 성공 (%d자)", len(text))

            ingredients_raw, steps_raw = split_youtube_description(text)
            if not ingredients_raw:
                return None

            return self._build_result("YouTube 레시피", image_url, ingredients_raw, steps_raw)

        except Exception as exc:
            logger.warning("[YouTube] 자막 실패: %s", exc)
            return None

    def _build_result(
        self,
        title: str,
        image_url: str | None,
        ingredients_raw: list[str],
        steps_raw: list[str],
    ) -> ScrapeResult:
        ingredients = [
            ScrapedIngredient(**parse_ingredient_line(normalize_string(r)))
            for r in ingredients_raw
        ]
        steps = [
            ScrapedStep(step_number=i, instruction=normalize_string(s))
            for i, s in enumerate(steps_raw, 1)
            if normalize_string(s)
        ]
        return ScrapeResult(
            title=title,
            image_url=image_url,
            source_url=self.url,
            source_type="youtube",
            ingredients=ingredients,
            steps=steps,
            scrape_success=bool(ingredients or steps),
        )
