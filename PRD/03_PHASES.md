# NyamNyamBook v2 — Phase 분리 계획

> 한 번에 다 만들면 복잡해져서 품질이 떨어집니다.
> Phase별로 나눠서 각각 "진짜 동작하는 제품"을 만듭니다.

---

## Phase 1: MVP (핵심)

### 목표
URL 하나로 레시피를 저장하고, 검색·태그·필터로 관리하며, 요리 횟수를 추적할 수 있는 완전한 서비스.

### Backend (FastAPI + Railway)

- [ ] 프로젝트 초기 세팅 (FastAPI, SQLAlchemy 2.0, Alembic)
- [ ] PostgreSQL DB 스키마 생성 (Supabase)
- [ ] Alembic 마이그레이션 설정
- [ ] Supabase Auth 연동 (JWT 검증 미들웨어)
- [ ] 레시피 CRUD API (`GET/POST/PUT/DELETE /recipes`)
- [ ] URL 스크래핑 API (`POST /scrape`)
  - recipe-scrapers 라이브러리 (일반 레시피 사이트)
  - 만개의레시피 전용 스크래퍼
  - 네이버 블로그 전용 스크래퍼
  - 자동 태그 생성 로직
- [ ] 재료 CRUD + 영한 매핑 검색 (`GET /ingredients`)
- [ ] 태그 CRUD (`GET/POST /tags`)
- [ ] 검색 API (`GET /recipes?q=소고기&tag=볶음&cooked=2`)
  - 다중키워드 AND 검색 (제목, 재료, 태그)
  - 태그 필터, 요리횟수 필터
- [ ] 요리 횟수 API (`POST /recipes/{id}/cook`)
  - `cooked_count` 증가 + `cook_logs` 기록
- [ ] 이미지 업로드 API (Supabase Storage)

### Frontend (Flutter Web + Vercel)

- [ ] Flutter Web 프로젝트 초기 세팅
- [ ] Supabase Auth 연동 (Google 소셜 로그인)
- [ ] 랜딩 페이지 (서비스 소개 + 로그인 버튼)
- [ ] 대시보드 화면
  - 레시피 카드 그리드
  - 검색창
  - 태그 필터 칩
  - 요리횟수 상태 필터 (도전예정/1회+/2회++/3회이상+++)
- [ ] 레시피 상세 화면
  - 이미지, 제목, 출처 링크, 시간, 재료, 조리단계, 태그
  - "요리했어요" 버튼 + 횟수 뱃지
- [ ] 레시피 추가 화면
  - URL 입력 탭 (스크래핑)
  - 직접 입력 탭
- [ ] 레시피 편집 화면
- [ ] 이미지 업로드 UI

### 데이터 (Phase 1에서 사용하는 테이블)
- `users` / `recipes` / `recipe_steps` / `recipe_ingredients` / `ingredients` / `recipe_tags` / `tags` / `cook_logs`

### 인증
- Supabase Auth (Google OAuth)

### "진짜 제품" 체크리스트
- [ ] 실제 Supabase DB 연결 (목업 데이터 X)
- [ ] 실제 Supabase Auth (하드코딩된 사용자 X)
- [ ] Railway에 FastAPI 배포 완료 (localhost X)
- [ ] Vercel에 Flutter Web 배포 완료
- [ ] 다른 사람이 URL로 접속해서 써볼 수 있음

### Phase 1 시작 프롬프트
```
이 PRD를 읽고 Phase 1을 구현해주세요.
@PRD/01_PRD.md
@PRD/02_DATA_MODEL.md
@PRD/04_PROJECT_SPEC.md

Phase 1 범위:
- FastAPI 백엔드: 인증, 레시피 CRUD, URL 스크래핑(웹/네이버/만개의레시피), 검색/태그/필터, 요리횟수
- Flutter Web 프론트: 랜딩, 대시보드, 레시피 상세/추가/편집
- DB: Supabase PostgreSQL (02_DATA_MODEL.md 스키마 그대로)

반드시 지켜야 할 것:
- 04_PROJECT_SPEC.md의 "절대 하지 마" 목록 준수
- JSON 컬럼 절대 사용 금지 (recipe_steps, recipe_ingredients, recipe_tags 테이블 사용)
- 실제 Supabase 연결 (목업 데이터 X)
- 실제 Supabase Auth (하드코딩 X)
- 저작권: 레시피 공유 기능 만들지 말 것, source_url 표시만 허용
```

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
| Phase 1 (MVP) | 소셜로그인, CRUD, 스크래핑(웹/네이버/만개의레시피), 검색/태그/필터, 요리횟수 | 시작 전 |
| Phase 2 (확장) | YouTube/Instagram 스크래핑, 장보기, 공개/비공개, 무한스크롤, Rate Limiting | Phase 1 완료 후 |
| Phase 3 (고도화) | 링크공유, 인분계산, 평점/후기, PWA, 모바일 앱 | Phase 2 완료 후 |
