# Flask → FastAPI 스크래퍼 포팅 가이드

## 1. HTTP 클라이언트 변환 패턴

### requests → httpx 기본 변환

```python
# Flask (동기)
import requests

def scrape(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return parse(response.text)

# FastAPI (async)
import httpx

async def scrape(url: str) -> dict | None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
        except (httpx.TimeoutException, httpx.HTTPStatusError):
            return None
    return parse(response.text)
```

### Session 변환 (쿠키 유지)

```python
# Flask (동기 Session)
session = requests.Session()
session.headers.update(HEADERS)
response = session.get(url)

# FastAPI (async Session)
async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
    response = await client.get(url)
    # 쿠키는 client 객체가 자동 유지
```

### 리다이렉트 처리 (네이버 블로그)

```python
# 네이버 블로그는 리다이렉트가 많음
async with httpx.AsyncClient(
    headers=HEADERS,
    follow_redirects=True,  # 자동 리다이렉트 따라가기
    timeout=30.0
) as client:
    response = await client.get(url)
```

---

## 2. 클래스 구조 (base.py 인터페이스)

모든 FastAPI 스크래퍼는 `app/scrapers/base.py`의 `BaseScraper`를 상속해야 합니다.

```python
# app/scrapers/base.py (이미 존재, 수정 금지)
from abc import ABC, abstractmethod
from app.schemas.recipe import ScrapedRecipe

class BaseScraper(ABC):
    headers = {
        "User-Agent": "Mozilla/5.0 ...",
        "Accept-Language": "ko-KR,ko;q=0.9",
    }

    @abstractmethod
    async def scrape(self, url: str) -> ScrapedRecipe | None:
        """URL에서 레시피를 스크래핑합니다. 실패 시 None 반환."""
        ...
```

각 스크래퍼 구현:

```python
# app/scrapers/recipe10000.py
from app.scrapers.base import BaseScraper
from app.schemas.recipe import ScrapedRecipe

class Recipe10000Scraper(BaseScraper):
    async def scrape(self, url: str) -> ScrapedRecipe | None:
        async with httpx.AsyncClient(
            headers=self.headers, timeout=30.0
        ) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
            except httpx.TimeoutException:
                return None
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                raise

        soup = BeautifulSoup(response.text, 'html.parser')
        return self._parse(soup, url)

    def _parse(self, soup: BeautifulSoup, url: str) -> ScrapedRecipe | None:
        # 파싱 로직은 동기 OK (CPU 연산)
        title = soup.select_one('.view2_summary h3')
        if title is None:
            return None  # 파싱 실패 → None 반환

        return ScrapedRecipe(
            title=title.text.strip(),
            source_url=url,
            # ... 나머지 필드
        )
```

---

## 3. 에러 처리 원칙

| 에러 상황 | 처리 방법 | 사용자 경험 |
|-----------|-----------|-------------|
| 타임아웃 | `return None` | "수동 입력 폼" 표시 |
| 404 Not Found | `return None` | "수동 입력 폼" 표시 |
| 403 Forbidden | `return None` | "수동 입력 폼" 표시 |
| 파싱 실패 (셀렉터 없음) | `return None` | "수동 입력 폼" 표시 |
| 5xx 서버 에러 | `raise HTTPException(502)` | "잠시 후 다시 시도해주세요" |
| 잘못된 URL 형식 | `raise HTTPException(422)` | "올바른 URL을 입력해주세요" |

**핵심 원칙:** 스크래핑 실패는 절대 앱 크래시로 이어지면 안 됩니다. 항상 빈 폼으로 폴백.

---

## 4. URL 정규화

각 사이트는 모바일/PC URL이 다를 수 있습니다.

```python
def normalize_url(url: str) -> str:
    """모바일 URL을 PC URL로 정규화"""
    # 만개의레시피: m.10000recipe.com → www.10000recipe.com
    url = url.replace("m.10000recipe.com", "www.10000recipe.com")

    # 네이버 블로그: m.blog.naver.com → blog.naver.com
    url = url.replace("m.blog.naver.com", "blog.naver.com")

    return url
```

---

## 5. 환경변수 처리

```python
# Before (Flask, 금지)
SCRAPING_API_KEY = "실제키값"
DATABASE_URL = "postgresql://user:pass@host/db"

# After (FastAPI, Pydantic BaseSettings)
# app/config.py에서 가져오기
from app.config import settings

api_key = settings.SCRAPING_API_KEY  # .env 파일에서 자동 로드
```

`app/config.py` 예시:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    DATABASE_URL: str
    SCRAPING_API_KEY: str = ""  # Phase 2에서 필요

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 6. 인코딩 처리

네이버 블로그 등 일부 사이트는 인코딩 명시가 필요합니다.

```python
# httpx는 Content-Type 헤더에서 인코딩 자동 감지
# 그러나 실패 시 명시적 지정
response_text = response.content.decode('utf-8', errors='replace')
# 또는
response_text = response.text  # httpx 자동 처리 (대부분 OK)
```

---

## 7. 테스트 URL 목록

각 스크래퍼 테스트에 사용할 검증된 URL:

### 만개의레시피 (recipe10000.py)
```
https://www.10000recipe.com/recipe/6830868
https://www.10000recipe.com/recipe/6956838
https://www.10000recipe.com/recipe/6968765
https://www.10000recipe.com/recipe/7026234
https://www.10000recipe.com/recipe/6935029
```

### 네이버 블로그 (naver.py)
검증은 수동으로 진행 권장 (봇 감지 우회 필요할 수 있음)
```
# 테스트 전 먼저 브라우저로 접근 가능한지 확인
https://blog.naver.com/...
```
