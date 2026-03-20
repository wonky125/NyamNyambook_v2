# NyamNyamBook v2 — Phase 분리 계획

> 한 번에 다 만들면 복잡해져서 품질이 떨어집니다.
> Phase별로 나눠서 각각 "진짜 동작하는 제품"을 만듭니다.

---

## Phase 1: MVP (핵심)

> **현재 상태**: 구현 진행 중 (2026-03-20 기준)
> **프론트엔드 변경**: Flutter Web → **React + TypeScript + Vite** (결정 변경)

### 목표
URL 하나로 레시피를 저장하고, 검색·태그·필터로 관리하며, 요리 횟수를 추적할 수 있는 완전한 서비스.

### Backend (FastAPI + Railway)

- [x] 프로젝트 초기 세팅 (FastAPI, SQLAlchemy 2.0, Alembic)
- [x] PostgreSQL DB 스키마 생성 (Supabase, Alembic 마이그레이션 완료)
- [x] Supabase Auth 연동 (JWT 검증 — ES256/JWKS 방식, HS256 폴백 포함)
- [x] 레시피 CRUD API (`GET/POST/PUT/DELETE /recipes`) — 재료/단계/태그 포함
- [x] URL 스크래핑 API (`POST /scrape`)
  - [x] Schema.org 파서 (일반 레시피 사이트 — schema_org.py)
  - [x] 만개의레시피 전용 스크래퍼 (100% 파싱 확인)
  - [~] 네이버 블로그 스크래퍼 — **제목/이미지만 파싱, 재료/단계는 수동 입력 폴백** (블로그 구조 비정형으로 완전 파싱 포기)
  - [x] 자동 태그 생성 로직 (auto_tagger.py)
- [x] 태그 CRUD (`GET/POST /tags`)
- [x] 검색 API (`GET /search?q=소고기`)
- [x] 요리 횟수 API (`POST /recipes/{id}/cook`)
- [x] 이미지 업로드 API (`POST /images` — Supabase Storage)

### Frontend (React + TypeScript + Vite + Vercel)

> ⚠️ Flutter Web에서 React + TypeScript + Vite로 변경됨

- [x] React + TypeScript + Vite 프로젝트 세팅
- [x] Supabase Auth 연동 (Google 소셜 로그인)
- [x] 랜딩 페이지 (서비스 소개 + 로그인 버튼)
- [x] 대시보드 화면
  - [x] 레시피 카드 그리드
  - [x] 검색창 (실시간 검색)
  - [x] 에러 상태 처리
  - [ ] **태그 필터 칩** ← 미구현
  - [ ] **요리횟수 상태 필터** ← 미구현
- [x] 레시피 상세 화면 (이미지, 제목, 출처 링크, 재료, 조리단계, 태그, "요리했어요" 버튼)
- [x] 레시피 추가 화면 (URL 스크래핑 + 직접 입력 + 태그 제안 UI)
- [x] 레시피 편집 화면 (재료·조리단계·태그 편집 포함)
- [ ] **이미지 업로드 UI** ← 미구현

### 데이터 (Phase 1에서 사용하는 테이블)
- `recipes` / `recipe_steps` / `recipe_ingredients` / `ingredients` / `recipe_tags` / `tags` / `cook_logs`

### 인증
- Supabase Auth (Google OAuth, ES256 JWKS 방식)

### "진짜 제품" 체크리스트
- [x] 실제 Supabase DB 연결 (목업 데이터 X)
- [x] 실제 Supabase Auth (하드코딩된 사용자 X)
- [ ] Railway에 FastAPI 배포 완료 (localhost X)
- [ ] Vercel에 React Web 배포 완료
- [ ] 다른 사람이 URL로 접속해서 써볼 수 있음

---

## Phase 2: 확장

### 전제 조건
- Phase 1이 Vercel + Railway에 안정적으로 배포된 상태

### 목표
유튜브·인스타그램 스크래핑 추가, 장보기 리스트, 대용량 처리 안정화.

### 기능
- [ ] YouTube 스크래퍼 (영상 자막 추출 → 레시피 파싱)
- [ ] Instagram 스크래퍼 (ScrapingBee API 활용)
- [ ] 장보기 리스트 (레시피에서 재료 한번에 추가, 체크/삭제)
- [ ] 레시피 공개/비공개 설정 (`is_public` 컬럼)
- [ ] 벌크 URL 임포트 (여러 URL 한번에)
- [ ] 무한스크롤 + 페이지네이션 (현재: 전체 로드)
- [ ] Rate Limiting (스크래핑 API 보호)
- [ ] 비밀번호 재설정 (이메일, Supabase Auth)
- [ ] Kakao 소셜 로그인 추가

### 추가 데이터
- `shopping_items` 테이블 활성화

### 통합 테스트
- Phase 1 기능(스크래핑, 검색, 요리횟수)이 여전히 정상 동작하는지 확인

---

## Phase 3: 고도화

### 전제 조건
- Phase 1 + 2가 안정적으로 운영 중

### 목표
사용자 경험 고도화, 데이터 활용, 모바일 확장.

### 기능
- [ ] 원본 링크 공유 (source_url만 공유, 레시피 콘텐츠 공유 X)
- [ ] 인분 자동 계산 + 단위 변환 (g↔oz, 인분 조절 시 재료량 계산)
- [ ] cook_logs 평점(1-5점) + 후기 메모
- [ ] PWA (Progressive Web App) — 오프라인 저장, 홈화면 추가
- [ ] Flutter 모바일 빌드 (Android/iOS)
- [ ] Sentry 에러 모니터링
- [ ] CI/CD 파이프라인 (GitHub Actions)

### 주의사항
- 인분 계산 시 재료 단위 통일 필요 (amount/unit 컬럼 데이터 품질에 의존)
- 모바일 앱은 앱스토어 심사 기간 고려 (iOS 최대 2-3주)

---

## Phase 로드맵 요약

| Phase | 핵심 기능 | 상태 |
|-------|----------|------|
| Phase 1 (MVP) | 소셜로그인, CRUD, 스크래핑(웹/네이버/만개의레시피), 검색/태그/필터, 요리횟수 | **구현 중** (배포 전) |
| Phase 2 (확장) | YouTube/Instagram 스크래핑, 장보기, 공개/비공개, 무한스크롤, Rate Limiting | Phase 1 완료 후 |
| Phase 3 (고도화) | 링크공유, 인분계산, 평점/후기, PWA, 모바일 앱 | Phase 2 완료 후 |
