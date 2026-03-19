#!/usr/bin/env python3
"""
NyamNyamBook v2 스크래퍼 파싱 성공률 자동 테스트
변환된 FastAPI 스크래퍼의 파싱 성공률 80% 기준을 검증합니다.
"""
import sys
import json
import asyncio
import importlib.util
import argparse
from pathlib import Path


# 각 스크래퍼별 테스트 URL
TEST_URLS = {
    "recipe10000": [
        "https://www.10000recipe.com/recipe/6830868",
        "https://www.10000recipe.com/recipe/6956838",
        "https://www.10000recipe.com/recipe/6968765",
        "https://www.10000recipe.com/recipe/7026234",
        "https://www.10000recipe.com/recipe/6935029",
    ],
    "naver": [
        # 네이버 블로그는 수동으로 URL을 채워야 합니다 (봇 감지)
        # 아래 URL을 실제 레시피 블로그 URL로 교체하세요
        "REPLACE_WITH_NAVER_BLOG_URL_1",
        "REPLACE_WITH_NAVER_BLOG_URL_2",
        "REPLACE_WITH_NAVER_BLOG_URL_3",
    ],
}

# 파싱 성공의 최소 조건 (이 필드가 있어야 성공으로 간주)
REQUIRED_FIELDS = ["title"]
OPTIONAL_FIELDS = ["ingredients", "steps", "total_time", "source_url"]


def load_scraper_class(scraper_file: str, class_name: str):
    """스크래퍼 파일에서 클래스를 동적으로 로드합니다."""
    spec = importlib.util.spec_from_file_location("scraper_module", scraper_file)
    if spec is None or spec.loader is None:
        print(f"ERROR: 모듈을 로드할 수 없습니다: {scraper_file}", file=sys.stderr)
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"ERROR: 모듈 실행 실패: {e}", file=sys.stderr)
        sys.exit(1)

    if not hasattr(module, class_name):
        print(f"ERROR: 클래스 '{class_name}'를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    return getattr(module, class_name)


def detect_scraper_type(scraper_file: str) -> str:
    """파일명으로 스크래퍼 타입 자동 감지."""
    filename = Path(scraper_file).stem.lower()
    if "recipe10000" in filename or "10000" in filename:
        return "recipe10000"
    elif "naver" in filename:
        return "naver"
    return "recipe10000"  # 기본값


async def test_single_url(scraper_instance, url: str) -> dict:
    """단일 URL 파싱 테스트."""
    if "REPLACE_WITH" in url:
        return {
            "url": url,
            "success": False,
            "error": "테스트 URL이 설정되지 않음. scripts/test_parsing.py에서 URL을 교체하세요.",
            "fields_found": [],
        }

    try:
        result = await asyncio.wait_for(
            scraper_instance.scrape(url),
            timeout=30.0  # 30초 타임아웃
        )

        if result is None:
            return {"url": url, "success": False, "error": "scrape() returned None", "fields_found": []}

        # result가 dict인지 Pydantic model인지 처리
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
        elif hasattr(result, '__dict__'):
            result_dict = vars(result)
        else:
            result_dict = result

        fields_found = []
        for field in REQUIRED_FIELDS + OPTIONAL_FIELDS:
            value = result_dict.get(field)
            if value and (not isinstance(value, (list, str)) or len(value) > 0):
                fields_found.append(field)

        # 필수 필드가 있어야 성공
        success = all(f in fields_found for f in REQUIRED_FIELDS)

        return {
            "url": url,
            "success": success,
            "error": None,
            "fields_found": fields_found,
            "title": result_dict.get("title", "")[:50] if success else "",
        }

    except asyncio.TimeoutError:
        return {"url": url, "success": False, "error": "타임아웃 (30초 초과)", "fields_found": []}
    except Exception as e:
        return {"url": url, "success": False, "error": str(e)[:100], "fields_found": []}


async def run_tests(scraper_file: str, class_name: str, threshold: int, output_json: bool):
    """모든 테스트 URL에 대해 파싱 성공률을 측정합니다."""
    scraper_type = detect_scraper_type(scraper_file)
    test_urls = TEST_URLS.get(scraper_type, TEST_URLS["recipe10000"])

    print(f"\n파싱 성공률 테스트: {scraper_file}")
    print(f"스크래퍼 타입: {scraper_type} ({len(test_urls)}개 URL 테스트)")
    print("=" * 50)

    # 스크래퍼 클래스 로드
    ScraperClass = load_scraper_class(scraper_file, class_name)
    scraper = ScraperClass()

    # 순차 테스트 (너무 빠른 요청으로 봇 감지 방지)
    results = []
    for i, url in enumerate(test_urls, 1):
        print(f"[{i}/{len(test_urls)}] 테스트 중: {url[:60]}...")
        result = await test_single_url(scraper, url)
        results.append(result)

        # 다음 요청 전 잠시 대기 (봇 감지 방지)
        if i < len(test_urls):
            await asyncio.sleep(1.5)

    # 결과 집계
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    success_rate = len(successes) / len(results) * 100 if results else 0

    if output_json:
        output = {
            "total": len(results),
            "success": len(successes),
            "failure": len(failures),
            "success_rate": round(success_rate, 1),
            "threshold": threshold,
            "passed": success_rate >= threshold,
            "results": results,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return success_rate >= threshold

    # 텍스트 출력
    print(f"\n파싱 성공률 테스트 결과:")
    print(f"총 {len(results)}개 URL 테스트")
    print(f"성공: {len(successes)}개 ({success_rate:.0f}%)")
    print(f"실패: {len(failures)}개")

    if successes:
        print(f"\n✅ 성공 항목:")
        for r in successes:
            print(f"  - {r['url'][:60]}")
            print(f"    제목: {r.get('title', '(없음)')}")
            print(f"    파싱된 필드: {', '.join(r['fields_found'])}")

    if failures:
        print(f"\n❌ 실패 항목:")
        for r in failures:
            print(f"  - {r['url'][:60]}")
            print(f"    원인: {r['error']}")

    print(f"\n기준: {threshold}% / 달성: {success_rate:.0f}%")
    if success_rate >= threshold:
        print(f"✅ 기준 통과! 포팅 성공.\n")
    else:
        print(f"❌ 기준 미달. 실패 항목의 셀렉터를 수정하세요.\n")

    return success_rate >= threshold


def main():
    parser = argparse.ArgumentParser(description="스크래퍼 파싱 성공률 테스트")
    parser.add_argument("--scraper-file", required=True, help="변환된 스크래퍼 파일 경로")
    parser.add_argument("--class-name", required=True, help="스크래퍼 클래스 이름")
    parser.add_argument("--threshold", type=int, default=80, help="성공률 기준 (기본: 80)")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
    args = parser.parse_args()

    passed = asyncio.run(
        run_tests(args.scraper_file, args.class_name, args.threshold, args.json)
    )

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
