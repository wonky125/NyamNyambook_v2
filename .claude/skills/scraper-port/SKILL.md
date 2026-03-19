---
name: scraper-port
description: This skill should be used when the user asks to port, convert, or migrate Flask scrapers to FastAPI async — including "스크래퍼 포팅해줘", "Flask 코드 FastAPI로 바꿔줘", "기존 스크래퍼 변환해줘", "scraper port", "포팅 시작", "스크래퍼 옮겨줘", "기존 코드 재활용". Use this skill whenever existing scraper code (recipe10000.py, naver.py, youtube.py, instagram.py) needs to be converted to async FastAPI format — even if the user doesn't explicitly say "port". This skill enforces NyamNyamBook v2 DO NOT rules and validates 80%+ parsing success rate automatically.
---

# scraper-port

> 기존 Flask 스크래퍼를 FastAPI async 구조로 자동 변환하고, 파싱 성공률 80% 기준을 자동 검증합니다.

## 워크플로우

### Step 1: 파일 분석 (prompt)

Read the target Flask scraper file. If no path is given, check `C:\Users\Kayeon\Desktop\recipe-app\app\scrapers\` and suggest available files:
- `recipe10000.py` — 만개의레시피 스크래퍼
- `naver.py` — 네이버 블로그 스크래퍼
- `youtube.py` — YouTube 스크래퍼 (Phase 2)
- `instagram.py` — Instagram 스크래퍼 (Phase 2)

Read the source file and extract:
- HTTP client used (`requests`, `requests.Session`, `urllib`)
- BeautifulSoup selectors and parsing targets (title, ingredients, steps, time, image)
- Return data structure (dict keys, field names, types)
- Error handling patterns (try/except, status code checks)
- Any hardcoded values, URLs, or environment variable usage
- Flask-specific patterns (`@login_required`, `current_user`, `session`)

Output a structured analysis before proceeding:
```
분석 결과:
- HTTP 클라이언트: requests (동기)
- 파싱 대상: [제목, 재료, 조리순서, 시간, 이미지]
- 반환 타입: dict
- 에러 처리: try/except + status code
- 주의사항: [감지된 문제점]
```

### Step 2: DO NOT 규칙 검사 (review)

Before conversion, scan the source file for violations using `scripts/check_rules.py`:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/check_rules.py" <source_file_path>
```

Flag these patterns before proceeding:
- **JSON 컬럼**: `Column(JSON)`, `Column(JSONB)`, `_json =`, `json.dumps`, `json.loads` in DB context
- **환경변수 하드코딩**: JWT token patterns (`eyJ`), database URLs, API keys directly in code
- **DB 직접 초기화**: `db.create_all()`, `Base.metadata.create_all()`
- **Flask 인증 패턴**: `@login_required`, `current_user` as global, `session['user_id']`

If violations exist, show them and fix during conversion (or mark as TODO if complex).

### Step 3: FastAPI async 변환 (generate)

Convert following these rules. Read `references/porting-guide.md` for detailed patterns.

**HTTP 클라이언트 변환:**
```python
# Before (Flask/동기)
import requests
response = requests.get(url, headers=headers, timeout=10)

# After (FastAPI/async)
import httpx
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.get(url, headers=headers)
```

**클래스 구조 (base.py 인터페이스 준수):**
```python
from app.scrapers.base import BaseScraper
from app.schemas.recipe import ScrapedRecipe

class Recipe10000Scraper(BaseScraper):
    async def scrape(self, url: str) -> ScrapedRecipe | None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
            except httpx.TimeoutException:
                return None  # 폴백: 빈 폼으로 수동 입력
            except httpx.HTTPStatusError:
                return None

        soup = BeautifulSoup(response.text, 'html.parser')
        return self._parse(soup, url)

    def _parse(self, soup: BeautifulSoup, url: str) -> ScrapedRecipe | None:
        # 파싱 로직 (동기 OK — CPU 작업)
        ...
```

**환경변수 처리:**
```python
# Before: SCRAPING_API_KEY = "실제키값"
# After: from app.config import settings → settings.SCRAPING_API_KEY
```

**에러 처리 원칙:**
- `httpx.TimeoutException` → return `None` (사용자에게 수동 입력 폼 표시)
- `httpx.HTTPStatusError` → return `None` with logging
- Parsing failure → return partial `ScrapedRecipe` with empty optional fields
- Never raise exceptions that reach the user without Korean error messages

Generate the complete converted file at `app/scrapers/{scraper_name}.py`.
Print the full file content for review before writing.

### Step 4: 파싱 성공률 테스트 (script)

Run the parsing success rate test:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/test_parsing.py" \
  --scraper-file app/scrapers/{scraper_name}.py \
  --class-name {ScraperClassName} \
  --threshold 80
```

The script tests with 5 representative URLs per scraper type (defined in `scripts/test_parsing.py`).

Output format:
```
파싱 성공률 테스트 결과:
총 5개 URL 테스트
성공: 4개 (80%)
실패: 1개 (20%)

실패 항목:
- URL: https://... → 에러: CSS 셀렉터 '.recipe-title' 없음
  원인: 모바일 버전 URL (m.10000recipe.com)

권장 조치: 모바일/PC URL 자동 정규화 추가
```

If success rate < 80%, identify broken selectors and fix before proceeding.
Do not proceed to Step 5 until the 80% threshold is met or the user explicitly approves a lower rate.

### Step 5: 연결 코드 생성 (generate)

Generate integration code for `app/routers/scrape.py`:

```python
# app/routers/scrape.py에 추가
from app.scrapers.{scraper_name} import {ScraperClass}

def get_scraper(url: str) -> BaseScraper | None:
    """URL 패턴으로 적합한 스크래퍼 선택"""
    if "10000recipe.com" in url:
        return Recipe10000Scraper()
    elif "blog.naver.com" in url:
        return NaverBlogScraper()
    return None

@router.post("/scrape", response_model=ScrapedRecipe)
async def scrape_recipe_url(
    url: str,
    current_user: User = Depends(get_current_user)
):
    scraper = get_scraper(url)
    if scraper is None:
        raise HTTPException(status_code=422, detail="지원하지 않는 URL입니다.")

    result = await scraper.scrape(url)
    if result is None:
        raise HTTPException(
            status_code=422,
            detail="스크래핑에 실패했습니다. 직접 입력해주세요."
        )
    return result
```

Print final summary:
```
변환 완료!

원본: {source_file} (Flask, 동기)
변환: app/scrapers/{new_file} (FastAPI, async)
파싱 성공률: {X}% ({success}/{total})
DO NOT 규칙: {통과 / N개 경고}

다음 단계:
1. 위 연결 코드를 app/routers/scrape.py에 추가
2. pytest tests/ 로 전체 테스트 실행
3. uvicorn app.main:app --reload 로 로컬 확인
```

## References
- **`references/porting-guide.md`** — Flask→FastAPI 변환 패턴 상세 가이드 (requests→httpx, session 관리, 인증 패턴 등)

## Scripts
- **`scripts/check_rules.py`** — DO NOT 규칙 위반 정적 스캔 (JSON 컬럼, 환경변수, db.create_all 등)
- **`scripts/test_parsing.py`** — 테스트 URL로 파싱 성공률 자동 측정

## Settings
| 설정 | 기본값 | 변경 방법 |
|------|--------|-----------|
| 파싱 성공률 기준 | 80% | `--threshold 90` 인수로 변경 |
| 테스트 URL 수 | 5개 | `scripts/test_parsing.py`에서 URL 추가/변경 |
| HTTP 타임아웃 | 30초 | 변환 시 `httpx.AsyncClient(timeout=X)` 조정 |
| 소스 경로 기본값 | `C:\Users\Kayeon\Desktop\recipe-app\app\scrapers\` | Step 1에서 다른 경로 지정 가능 |
