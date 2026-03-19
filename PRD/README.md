# NyamNyamBook v2 — 디자인 문서

> Show Me The PRD로 생성됨 (2026-03-19)
> Flutter Web + FastAPI + Supabase 재설계 계획

---

## 문서 구성

| 문서 | 내용 | 언제 읽나 |
|------|------|----------|
| [01_PRD.md](./01_PRD.md) | 뭘 만드는지, 누가 쓰는지, 화면 구성 | 프로젝트 시작 전 / Figma 의뢰할 때 |
| [02_DATA_MODEL.md](./02_DATA_MODEL.md) | 9개 테이블 정규화 DB 스키마 | DB 설계할 때 / AI에게 코드 시킬 때 |
| [03_PHASES.md](./03_PHASES.md) | Phase별 기능 체크리스트 + 로드맵 | 개발 순서 정할 때 / 시작 프롬프트 |
| [04_PROJECT_SPEC.md](./04_PROJECT_SPEC.md) | 기술 스택, DO/DO NOT, 환경변수 | AI에게 코드 시킬 때마다 필수 첨부 |

---

## 핵심 결정사항 요약

| 항목 | 결정 |
|------|------|
| 플랫폼 | Flutter Web (Vercel) |
| 백엔드 | FastAPI (Railway) |
| DB | PostgreSQL (Supabase) |
| 인증 | Google 소셜 로그인 (Supabase Auth) |
| 이미지 | Supabase Storage |
| MVP 기능 | 스크래핑 + 검색/태그 + 요리횟수 |
| 저작권 | 레시피 콘텐츠 공유 X, source_url만 공유 |
| 밀프렙 | 제외 (사용자 결정) |
| 기존 데이터 | 이관 안 함, 새로 시작 |

---

## 다음 단계

### Phase 1 시작하기
[03_PHASES.md](./03_PHASES.md)의 **"Phase 1 시작 프롬프트"** 를 복사해서 AI에게 전달하세요.
반드시 이 파일들을 함께 첨부하세요:
- `@PRD/01_PRD.md`
- `@PRD/02_DATA_MODEL.md`
- `@PRD/04_PROJECT_SPEC.md`

### Figma 의뢰하기
[01_PRD.md](./01_PRD.md)의 **"5. 화면 구성"** 섹션을 Figma 디자이너에게 전달하세요.
6개 화면: 랜딩 / 대시보드 / 레시피 상세 / 레시피 추가 / 레시피 편집 / 프로필

---

## 미결 사항 종합

- [ ] Flutter 상태관리 라이브러리 선택 (Riverpod 추천)
- [ ] Supabase Auth: Google만 Phase 1? Kakao는 Phase 2?
- [ ] `ingredients` 시드 데이터: 기존 50+ 영한 매핑 이식 여부
- [ ] Railway 무료 크레딧 한도 초과 시 대안 플랫폼
- [ ] 태그 자동 생성 기준: 기존 7개 카테고리 그대로 사용 여부
