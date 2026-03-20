# NyamNyamBook v2 — Agent Handoff

> 이 파일 하나만 읽으면 바로 작업을 이어받을 수 있다.
> 작성일: 2026-03-20 (2세션 종합)

---

## 프로젝트 개요

URL 하나로 레시피를 저장하는 웹앱. **Phase 1 MVP 구현 + Vercel 배포 완료**.

- **Frontend**: React + TypeScript + Vite → Vercel 배포됨
- **Backend**: FastAPI + Python → Vercel Serverless 배포됨
- **DB**: Supabase PostgreSQL (Alembic 마이그레이션 완료)
- **인증**: Supabase Auth (Google OAuth, ES256/JWKS 방식)
- **GitHub**: `wonky125/NyamNyambook_v2`

---

## 배포 현황

| 서비스 | URL | 상태 |
|--------|-----|------|
| 백엔드 API | `https://nyamnyambook-api.vercel.app` | ✅ 배포 완료 |
| 프론트엔드 | `https://[프론트URL].vercel.app` | ✅ 배포 완료 |
| DB | Supabase PostgreSQL | ✅ 운영 중 |

> 백엔드 health check: `GET /health` → `{"status": "ok", "version": "1.0.0"}`

---

## 세션 1에서 한 일

### 1. JWT 인증 수정 ✅
- **문제**: 백엔드가 401 Unauthorized 반환
- **원인**: 최신 Supabase가 HS256 대신 ES256(ECDSA) 사용
- **해결**: `backend/app/dependencies.py`를 JWKS 방식으로 전면 교체
  - ES256이면 `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`에서 공개키 가져와 검증
  - HS256 폴백 유지 (구형 프로젝트 호환)
  - JWKS 모듈 레벨 `_jwks_cache`에 캐싱

### 2. 만개의레시피 스크래퍼 수정 ✅
- CSS 셀렉터가 실제 HTML과 불일치 → 전면 수정
- 테스트 결과: 5/5 URL 100% 성공

### 3. 네이버 블로그 스크래퍼 ⚠️ 포기 결정
- **시도**: `_split_blog_text()` 텍스트 파싱, se-component 구조 분석 등 여러 방법 시도
- **결론**: 블로거마다 HTML 구조가 달라 안정적 파싱 불가능, 시간 대비 실익 없음
- **현재 동작**: 제목 + 이미지만 파싱, 재료/단계는 빈 리스트 → 수동 입력 폴백 (CLAUDE.md 정책과 일치)

---

## 세션 2에서 한 일

### 4. 재료/단계가 상세 페이지에서 안 보이는 버그 수정 ✅
- **원인**: ORM 모델의 관계명 불일치
  - ORM: `recipe_ingredients`, `recipe_tags`
  - Pydantic 스키마: `ingredients`, `tags`
  - → Pydantic이 항상 빈 리스트 `[]` 반환
- **해결**: `backend/app/models/recipe.py`에 property 추가
  ```python
  @property
  def ingredients(self): return self.recipe_ingredients
  @property
  def tags(self): return self.recipe_tags
  ```

### 5. RecipeEdit 전면 재구현 ✅
- 기존: 제목/설명/인분/메모만 편집 가능
- 현재: 재료(textarea, 한 줄에 하나) + 조리단계(textarea, 줄바꿈 구분) + 태그 + 이미지 편집
- 프로토타입 스크린샷 참고해서 구현 (`.jfif` 파일들 프로젝트 루트에 있음)

### 6. RecipeAdd 태그 제안 UI ✅
- 스크래핑 결과의 `suggested_tags` → 클릭 가능한 칩으로 표시
- 저장 시 선택된 태그를 `POST /tags` (get_or_create) → ID 변환 → 레시피에 연결

### 7. 대시보드 필터 추가 ✅
- **태그 필터 칩**: 전체 태그 목록 표시, 클릭 시 백엔드 `tag_id` 필터링
- **요리횟수 필터**: 전체 / 도전 예정(0회) / 1회+ / 3회+ (클라이언트 사이드)
- **에러 처리**: `isError` 시 에러 메시지 표시

### 8. 이미지 업로드 UI ✅ (RecipeEdit)
- 점선 박스 클릭 → 파일 선택 → `POST /images` → Supabase Storage
- 이미지 있으면 미리보기 + 변경/삭제 버튼

### 9. Vercel 배포 ✅
- `backend/api/index.py` — Vercel ASGI 진입점
- `backend/vercel.json` — 모든 요청을 FastAPI로 라우팅
- `frontend/vercel.json` — SPA 라우팅 (react-router 대응)
- CORS를 `ALLOWED_ORIGINS` 환경변수로 관리
- **배포 방식**: 같은 GitHub 레포에서 백엔드/프론트 각각 별도 Vercel 프로젝트로 배포 (Root Directory 설정)

---

## 현재 파일 구조 (핵심만)

```
backend/
  api/index.py          ← Vercel 진입점 (from app.main import app)
  vercel.json           ← Vercel 라우팅 설정
  app/
    main.py             ← FastAPI 앱 (CORS: ALLOWED_ORIGINS 환경변수)
    config.py           ← Settings (ALLOWED_ORIGINS 추가됨)
    dependencies.py     ← JWT 인증 (JWKS ES256)
    models/recipe.py    ← ingredients/tags property 추가
    scrapers/
      recipe10000.py    ← 만개의레시피 (정상 작동)
      naver.py          ← 제목/이미지만 파싱, 재료/단계 포기
      schema_org.py     ← 범용 Schema.org 파서
    routers/
      recipes.py / scrape.py / search.py / tags.py / images.py / cook_logs.py

frontend/
  vercel.json           ← SPA 라우팅
  src/
    App.tsx             ← 라우팅
    hooks/
      useRecipes.ts     ← useRecipes, useRecipe, useTags, useUploadImage 등
      useAuth.ts
    pages/
      Dashboard.tsx     ← 태그필터 + 요리횟수필터 + 에러처리
      RecipeAdd.tsx     ← 스크래핑 + 태그제안 UI
      RecipeDetail.tsx  ← 상세 보기
      RecipeEdit.tsx    ← 재료/단계/태그/이미지 편집
      Landing.tsx
    types/index.ts
    lib/api.ts          ← Axios (Supabase 토큰 자동 첨부)
```

---

## 환경변수

### 백엔드 (Vercel 환경변수 + 로컬 backend/.env)
| 변수명 | 설명 |
|--------|------|
| `SUPABASE_URL` | Supabase 프로젝트 URL |
| `SUPABASE_KEY` | Service Role Key |
| `SUPABASE_JWT_SECRET` | JWT Secret (HS256 폴백용, 필수는 아님) |
| `DATABASE_URL` | `postgresql+asyncpg://...` |
| `SECRET_KEY` | 임의 랜덤 문자열 |
| `ENVIRONMENT` | `production` (Vercel) / `development` (로컬) |
| `ALLOWED_ORIGINS` | 프론트 URL (예: `https://nyamnyambook.vercel.app`) |

### 프론트엔드 (Vercel 환경변수 + 로컬 frontend/.env)
| 변수명 | 설명 |
|--------|------|
| `VITE_SUPABASE_URL` | Supabase URL |
| `VITE_SUPABASE_ANON_KEY` | Anon Key |
| `VITE_API_BASE_URL` | 백엔드 URL (로컬: `http://localhost:8000`) |

---

## 로컬 실행

```bash
# 백엔드
cd backend
uvicorn app.main:app --reload

# 프론트엔드
cd frontend
npm run dev
```

---

## 알려진 이슈 / 주의사항

### Vercel 서버리스 함수 타임아웃
- 무료 tier: **10초 제한**
- 스크래핑이 느린 사이트에서 간헐적 실패 가능
- 대부분 사이트는 3-5초 이내라 실용상 문제없음
- 유저 많아지면 Railway로 이사 예정 (환경변수 `VITE_API_BASE_URL` 하나만 바꾸면 됨)

### Supabase OAuth 설정 필수
- Google 로그인이 동작하려면 Supabase → Authentication → URL Configuration에서
  - Site URL: 프론트 Vercel URL
  - Redirect URLs: `https://[프론트URL].vercel.app/**`
  - 위 설정 안 하면 OAuth 리다이렉트 막힘

### 네이버 블로그 스크래핑
- 제목/이미지만 파싱, 재료/단계는 빈 리스트 반환
- 사용자가 편집 화면에서 직접 입력하는 방식으로 운영

---

## 다음에 할 일 (Phase 1 완성 후)

| 순위 | 작업 | 내용 |
|------|------|------|
| 1 | **Sentry 연동** | `sentry-sdk` 설치 후 백엔드/프론트 각각 연동 |
| 2 | **디자인 개선** | 인라인 style → Tailwind 또는 CSS 모듈, 반응형 |
| 3 | **Phase 2** | YouTube/Instagram 스크래핑, 장보기 리스트 |
| 4 | **Railway 이사** | 유저 생기면 `VITE_API_BASE_URL`만 바꾸면 됨 |
