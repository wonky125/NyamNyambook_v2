# NyamNyamBook v2 — 프로젝트 스펙

> AI가 코드를 짤 때 지켜야 할 규칙과 절대 하면 안 되는 것.
> 이 문서를 AI에게 항상 함께 공유하세요.

---

## 기술 스택

| 영역 | 선택 | 이유 |
|------|------|------|
| Frontend | ~~Flutter Web~~ → **React + TypeScript + Vite** | 개발 속도, 생태계. 모바일은 Phase 3에서 별도 검토 |
| Frontend 배포 | Vercel | React 정적 파일 무료 호스팅 |
| Backend | FastAPI (Python) | 기존 스크래핑 코드 재사용, async 지원 |
| Backend 배포 | Railway | 장기실행 서버 필요 (스크래핑), Git push 자동 배포 |
| DB | PostgreSQL (Supabase) | 무료 500MB, 관리 UI 편리, Row Level Security |
| 이미지 저장 | Supabase Storage | DB와 같은 플랫폼, 무료 1GB |
| 인증 | Supabase Auth (Google OAuth) | ES256/JWKS 방식으로 JWT 검증 |
| ORM | SQLAlchemy 2.0 | 기존 코드 기반, async 지원 |
| DB 마이그레이션 | Alembic | SQLAlchemy 표준 마이그레이션 도구 |

---

## 프로젝트 구조

### Backend (FastAPI)
```
backend/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 환경변수 설정
│   ├── database.py          # DB 연결, 세션
│   ├── models/              # SQLAlchemy 모델
│   │   ├── recipe.py
│   │   ├── ingredient.py
│   │   ├── tag.py
│   │   └── user.py
│   ├── routers/             # API 라우터
│   │   ├── recipes.py
│   │   ├── scrape.py
│   │   ├── search.py
│   │   └── auth.py
│   ├── scrapers/            # 스크래핑 모듈 (기존 코드 재활용)
│   │   ├── base.py
│   │   ├── recipe10000.py   # 만개의레시피
│   │   ├── naver.py         # 네이버 블로그
│   │   ├── youtube.py       # Phase 2
│   │   └── instagram.py     # Phase 2
│   ├── schemas/             # Pydantic 스키마
│   └── utils/
│       ├── auto_tagger.py   # 자동 태그 생성
│       └── ingredient_mapping.py  # 영한 매핑
├── migrations/              # Alembic 마이그레이션
├── .env                     # 환경변수 (절대 커밋 금지)
├── requirements.txt
└── Dockerfile
```

### Frontend (React + TypeScript + Vite)
```
frontend/
├── src/
│   ├── main.tsx             # 진입점
│   ├── App.tsx              # 라우팅 설정 (react-router-dom)
│   ├── pages/               # 화면
│   │   ├── Landing.tsx
│   │   ├── Dashboard.tsx
│   │   ├── RecipeDetail.tsx
│   │   ├── RecipeAdd.tsx
│   │   └── RecipeEdit.tsx
│   ├── hooks/               # React Query 훅
│   │   ├── useAuth.ts
│   │   └── useRecipes.ts
│   ├── lib/
│   │   └── api.ts           # Axios 인터셉터 (Supabase 토큰 자동 첨부)
│   └── types/
│       └── index.ts         # 타입 정의
├── index.html
├── vite.config.ts
├── package.json
└── .env                     # VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_BASE_URL
```

---

## 절대 하지 마 (DO NOT)

> AI에게 코드를 시킬 때 이 목록을 반드시 함께 공유하세요.

- [ ] **API 키나 비밀번호를 코드에 직접 쓰지 마** — .env 파일에 저장, .gitignore에 추가
- [ ] **JSON 컬럼 사용하지 마** — `tags_json`, `ingredients_json`, `steps_json` 같은 TEXT에 JSON 저장 금지. 반드시 정규화 테이블 사용
- [ ] **기존 DB 스키마를 임의로 변경하지 마** — 변경 필요 시 Alembic 마이그레이션 파일 작성 후 승인받기
- [ ] **목업/하드코딩 데이터로 완성이라고 하지 마** — 실제 Supabase DB 연결 필수
- [ ] **레시피 콘텐츠를 다른 사용자와 공유하는 기능 만들지 마** — 저작권 문제. `source_url` 링크만 공유 가능
- [ ] **밀프렙(식단 계획/캘린더) 기능 만들지 마** — 스펙에서 제외됨
- [ ] **커뮤니티/피드/레시피 공유 기능 만들지 마** — 저작권 이슈로 제외
- [ ] **package 버전을 임의로 변경하지 마** — 충돌 위험
- [ ] **Supabase RLS(Row Level Security)를 비활성화하지 마** — 보안 필수

---

## 항상 해 (ALWAYS DO)

- [ ] **변경하기 전에 계획을 먼저 보여줘** — 특히 DB 스키마 변경 시
- [ ] **환경변수는 .env 파일에 저장** — 절대 코드에 직접 쓰지 않기
- [ ] **에러 발생 시 사용자에게 친절한 한국어 메시지 표시**
- [ ] **모바일에서도 사용 가능한 반응형 디자인** (Flutter Web)
- [ ] **스크래핑 실패 시 수동 입력으로 폴백** — 파싱 실패해도 빈 폼 표시
- [ ] **Alembic으로 DB 마이그레이션 관리** — `db.create_all()` 직접 호출 금지

---

## 테스트 방법

```bash
# Backend 로컬 실행
cd backend
uvicorn app.main:app --reload

# FastAPI 자동 문서
http://localhost:8000/docs

# Frontend 로컬 실행
cd frontend
npm run dev
```

---

## 배포 방법

### Backend (Railway)
```bash
# Railway CLI
railway login
railway up

# 또는 GitHub 연결 후 git push로 자동 배포
git push origin main
```

### Frontend (Vercel)
```bash
# React 빌드
cd frontend
npm run build

# Vercel 배포 (빌드 결과물: dist/)
vercel --prod
```

---

## 환경변수

### Backend (.env)
| 변수명 | 설명 | 어디서 발급 |
|--------|------|------------|
| `SUPABASE_URL` | Supabase 프로젝트 URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Supabase Service Role Key | Supabase Dashboard → Settings → API |
| `SUPABASE_JWT_SECRET` | JWT 검증용 시크릿 | Supabase Dashboard → Settings → API |
| `DATABASE_URL` | PostgreSQL 연결 문자열 | Supabase Dashboard → Settings → Database |
| `SCRAPINGBEE_API_KEY` | Instagram 스크래핑용 (Phase 2) | scrapingbee.com |
| `SENTRY_DSN` | 에러 모니터링 (Phase 3) | sentry.io |

### Frontend (.env)
| 변수명 | 설명 |
|--------|------|
| `VITE_SUPABASE_URL` | Supabase 프로젝트 URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase Anon Key (공개 가능) |
| `VITE_API_BASE_URL` | FastAPI 서버 URL (Railway, 로컬: http://localhost:8000) |

> .env 파일은 절대 GitHub에 올리지 마세요. .gitignore에 추가 필수.

---

## 기존 코드 재활용 목록

기존 Flask 앱(`C:\Users\Kayeon\Desktop\recipe-app\app\`)에서 아래 로직을 FastAPI로 포팅:

| 기존 파일 | 재활용 내용 | 상태 |
|-----------|------------|------|
| `scrapers/recipe10000.py` | 만개의레시피 스크래퍼 | ✅ 포팅 완료 |
| `scrapers/naver.py` | 네이버 블로그 스크래퍼 | ⚠️ 제목/이미지만 파싱. 재료/단계는 블로그 비정형 구조 한계로 포기 → 수동 입력 폴백 |
| `scrapers/youtube.py` | YouTube 스크래퍼 (Phase 2) | Phase 2 |
| `scrapers/instagram.py` | Instagram 스크래퍼 (Phase 2) | Phase 2 |
| `utils/auto_tagger.py` | 자동 태그 생성 + 7개 카테고리 | ✅ 포팅 완료 |
| `utils/ingredient_mapping.py` | 영한 재료 매핑 50+ 항목 | ✅ 포팅 완료 |
| `scrapers/text_splitter.py` | 비정형 텍스트 파싱 | ⚠️ 네이버용으로만 사용, 효과 제한적 |

---

## [NEEDS CLARIFICATION]

- [ ] Supabase Auth: Kakao 로그인은 Phase 2?
- [ ] Railway 무료 크레딧 소진 시 대안 (Render, Fly.io)
