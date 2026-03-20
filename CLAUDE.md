# NyamNyamBook v2 — AI 작업 규칙

> 이 문서를 항상 먼저 읽어라. 모든 코드 작업 전에 이 규칙이 우선한다.

## 프로젝트

URL 하나로 레시피를 저장하고 관리하는 웹 서비스.
- **기술 스택**: React + TypeScript + Vite (프론트) + FastAPI (백엔드) + PostgreSQL/Supabase (DB)
- **PRD 전체**: `PRD/` 폴더 참조
- **현재 Phase**: Phase 1 (MVP) — `PRD/03_PHASES.md` 확인

---

## 최우선 목표: 스파게티 코드 방지

> 이 프로젝트에서 가장 중요한 원칙이다. 기능이 동작해도 구조가 엉키면 실패다.

### 파일 하나 = 역할 하나

각 파일은 딱 한 가지 일만 한다. 절대로 섞지 않는다.

**Backend 역할 분리:**
```
routers/     → URL 경로 정의 + 요청/응답만. DB 직접 쿼리 금지.
services/    → 비즈니스 로직만. DB 쿼리 + 규칙 처리.
models/      → DB 테이블 구조만. 로직 없음.
schemas/     → 입출력 데이터 형식만. 검증 규칙 포함.
scrapers/    → 스크래핑만. DB 저장 금지.
utils/       → 재사용 함수만. 특정 기능에 종속되면 안 됨.
```

**Frontend 역할 분리:**
```
pages/       → UI 화면만. 데이터 처리 로직 금지.
hooks/       → React Query 훅. API 호출 + 상태 관리.
lib/         → Axios 클라이언트 등 공통 유틸.
types/       → 타입 정의만.
```

### 역할을 섞으면 안 되는 예시

```python
# ❌ 스파게티: router에서 DB 직접 쿼리
@router.get("/recipes")
async def get_recipes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recipe).where(...))  # 여기서 하면 안 됨
    return result

# ✅ 올바른 구조: router는 service를 호출
@router.get("/recipes")
async def get_recipes(current_user = Depends(get_current_user), service = Depends(RecipeService)):
    return await service.get_user_recipes(current_user.id)
```

```dart
// ❌ 스파게티: screen에서 API 직접 호출
class DashboardScreen extends StatelessWidget {
  Future<void> _loadRecipes() async {
    final response = await http.get(...);  // screen에서 하면 안 됨
  }
}

// ✅ 올바른 구조: screen은 provider를 통해 데이터 접근
class DashboardScreen extends ConsumerWidget {
  Widget build(BuildContext context, WidgetRef ref) {
    final recipes = ref.watch(recipesProvider);  // provider 사용
  }
}
```

### 파일이 200줄을 넘으면 분리 신호

- 200줄 초과 → 역할이 두 개 이상 섞인 것. 파일을 쪼개야 한다.
- 단, 모델 파일은 예외 (컬럼이 많을 수 있음).

---

## DB 규칙 (절대 금지)

> 이 규칙을 어기면 나중에 전체를 다시 짜야 한다.

1. **JSON 컬럼 금지** — `Column(JSON)`, `Column(JSONB)`, `_json` 변수명 사용 금지
   - 대신 정규화 테이블 사용: `recipe_steps`, `recipe_ingredients`, `recipe_tags`
   - 이유: JSON 컬럼은 검색이 느리고 나중에 수정이 불가능에 가깝다

2. **DB 변경 전 계획 먼저 보여줘** — 실행 전에 무엇을 바꾸는지 표로 출력
   - 이유: 한 번 잘못 바꾼 DB는 되돌리기 어렵다

3. **Alembic으로만 마이그레이션** — `db.create_all()` / `Base.metadata.create_all()` 절대 금지
   - 올바른 방법: `alembic revision --autogenerate` → `alembic upgrade head`
   - 이유: 직접 생성하면 마이그레이션 이력이 망가져서 팀 작업이 불가능해진다

4. **데이터 모델**: `PRD/02_DATA_MODEL.md` 그대로 구현. 임의 변경 금지

→ DB 변경이 필요하면 `db-migrate` 스킬을 사용한다.

---

## 보안 규칙 (절대 금지)

1. **환경변수 코드에 직접 쓰지 마** — `.env` 파일에만 저장
   - 금지: `SUPABASE_KEY = "eyJh..."` (코드 안에 직접)
   - 허용: `settings.SUPABASE_KEY` (config.py의 BaseSettings 사용)

2. **Supabase RLS 끄지 마** — Row Level Security는 항상 활성화
   - 이유: 끄면 다른 사용자의 레시피가 노출된다

3. **인증 없이 데이터 변경 허용하지 마** — 모든 POST/PUT/DELETE에 `Depends(get_current_user)` 필수

---

## Phase 경계 (섞지 마)

지금은 **Phase 1**만 만든다. Phase 2/3 기능을 먼저 만들면 코드가 복잡해진다.

| Phase | 포함 | 제외 |
|-------|------|------|
| **Phase 1 (지금)** | 로그인, 레시피 CRUD, 스크래핑(웹/네이버/만개의레시피), 검색, 태그, 요리횟수 | YouTube/Instagram 스크래핑, 장보기, 공개/비공개 |
| Phase 2 (나중) | YouTube/Instagram, 장보기, 무한스크롤 | — |
| Phase 3 (나중) | 평점/후기, 인분계산, 모바일 앱 | — |

Phase 2/3 기능을 요청받으면: "지금은 Phase 1 범위가 아닙니다. Phase 1 완료 후 진행하겠습니다." 라고 알린다.

---

## 스크래핑 규칙

1. 스크래핑 실패 = 앱 오류가 아니다 → 빈 입력 폼으로 폴백 (사용자가 직접 입력)
2. Flask 스크래퍼 코드를 FastAPI로 포팅할 때 → `scraper-port` 스킬 사용
3. 기존 Flask 코드 위치: `C:\Users\Kayeon\Desktop\recipe-app\app\scrapers\`
4. 저작권: 레시피 콘텐츠를 다른 사용자와 공유하는 기능 만들지 말 것. `source_url` 링크만 허용

---

## 사용 가능한 스킬

프로젝트 전용 자동화 도구가 `.claude/skills/`에 있다.

| 스킬 | 언제 | 트리거 키워드 |
|------|------|--------------|
| `db-migrate` | DB 테이블/컬럼을 추가하거나 바꿀 때 | "테이블 추가", "컬럼 바꿔줘", "DB 수정", "마이그레이션" |
| `scraper-port` | Flask 스크래퍼를 FastAPI로 옮길 때 | "포팅해줘", "스크래퍼 변환", "기존 코드 재활용" |

---

## 작업 전 체크리스트

코드를 작성하기 전에 반드시 확인:

- [ ] 이 기능이 Phase 1 범위인가? (`PRD/03_PHASES.md`)
- [ ] 파일 위치가 `PRD/04_PROJECT_SPEC.md`의 구조와 맞는가?
- [ ] DB를 바꾸는가? → 계획 먼저 보여주고, Alembic 사용
- [ ] 환경변수가 코드에 직접 쓰여 있지 않은가?
- [ ] JSON 컬럼을 쓰려 하지 않는가?
- [ ] 새 파일의 역할이 하나로 명확한가?

---

## 참고 문서

| 문서 | 내용 |
|------|------|
| `PRD/01_PRD.md` | 제품 개요, 사용자 시나리오, 성공 기준 |
| `PRD/02_DATA_MODEL.md` | DB 테이블 구조 (이게 정답, 임의 변경 금지) |
| `PRD/03_PHASES.md` | Phase별 기능 범위 |
| `PRD/04_PROJECT_SPEC.md` | 기술 스택, 폴더 구조, DO NOT 목록 |
