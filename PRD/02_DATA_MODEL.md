# NyamNyamBook v2 — 데이터 모델

> 이 문서는 앱에서 다루는 핵심 데이터의 구조를 정의합니다.
> JSON 컬럼을 완전 제거하고 모든 데이터를 정규화한 버전입니다.

---

## 전체 구조

```
users (회원)
│
├─ 1:N ─ recipes (레시피)
│          │
│          ├─ 1:N ─ recipe_steps    (조리 단계, 기존 steps_json 대체)
│          │
│          ├─ 1:N ─ recipe_ingredients ─ N:1 ─ ingredients (재료 사전)
│          │
│          ├─ M:N ─ recipe_tags        ─ N:1 ─ tags (태그 사전)
│          │
│          └─ 1:N ─ cook_logs          (요리 이력, cooked_count 상세화)
│
└─ 1:N ─ shopping_items (장보기 리스트, Phase 2)
```

---

## 엔티티 상세

### users (회원)
레시피를 저장하고 관리하는 사용자 계정.

| 필드 | 타입 | 예시 | 필수 |
|------|------|------|------|
| id | UUID (PK) | `a1b2c3d4-...` | O |
| email | VARCHAR(120) | `user@gmail.com` | O |
| password_hash | VARCHAR(200) | `$2b$12$...` | O |
| name | VARCHAR(100) | `요리왕짱구` | O |
| created_at | TIMESTAMPTZ | `2026-03-19T12:00:00Z` | O |
| updated_at | TIMESTAMPTZ | `2026-03-19T12:00:00Z` | O |

> **참고**: Supabase Auth를 사용하면 users 테이블은 Supabase가 관리.
> 추가 프로필 정보는 별도 `profiles` 테이블로 분리 가능.

---

### recipes (레시피)
사용자가 저장한 레시피. JSON 컬럼 완전 제거.

| 필드 | 타입 | 예시 | 필수 |
|------|------|------|------|
| id | SERIAL (PK) | `42` | O |
| user_id | UUID FK → users | `a1b2c3d4-...` | O |
| title | VARCHAR(200) | `간장계란볶음밥` | O |
| description | TEXT | `10분이면 완성되는 간단 볶음밥` | X |
| servings | VARCHAR(50) | `2인분` | X |
| prep_time | INT (분) | `5` | X |
| cook_time | INT (분) | `10` | X |
| total_time | INT (분) | `15` | X |
| image_url | TEXT | `https://supabase.../recipe.jpg` | X |
| source_url | TEXT | `https://youtu.be/abc123` | X |
| source_type | VARCHAR(20) | `youtube` / `web` / `naver` / `instagram` / `manual` | X |
| notes | TEXT | `간장 대신 굴소스도 맛있음` | X |
| cooked_count | INT | `3` | O (default 0) |
| is_public | BOOLEAN | `false` | O (default false) |
| created_at | TIMESTAMPTZ | `2026-03-19T12:00:00Z` | O |
| updated_at | TIMESTAMPTZ | `2026-03-19T12:00:00Z` | O |

**개선점 (vs 현재)**:
- `tags_json`, `ingredients_json`, `steps_json` 컬럼 완전 제거
- `prep_time`/`cook_time`/`total_time`을 문자열("10분")에서 정수(분 단위)로 변환
- `source_type`으로 출처 플랫폼 구분 가능

---

### recipe_steps (조리 단계) ★ 신규
기존 `steps_json` TEXT 컬럼을 정규화. 단계별 이미지 지원.

| 필드 | 타입 | 예시 | 필수 |
|------|------|------|------|
| id | SERIAL (PK) | `101` | O |
| recipe_id | INT FK → recipes | `42` | O |
| step_number | SMALLINT | `1` | O |
| instruction | TEXT | `팬을 달구고 기름을 두릅니다` | O |
| image_url | TEXT | `https://supabase.../step1.jpg` | X |

---

### ingredients (재료 사전)
재료 이름을 정규화한 공유 사전. 한글명 + 영문명으로 영한 검색 지원.

| 필드 | 타입 | 예시 | 필수 |
|------|------|------|------|
| id | SERIAL (PK) | `7` | O |
| name | VARCHAR(100) | `소고기` | O |
| name_en | VARCHAR(100) | `beef` | X |

**개선점**: 기존 `ingredient_mapping.py`의 50+ 매핑을 DB에 시드하여 관리.

---

### recipe_ingredients (레시피-재료 연결)
어떤 레시피에 어떤 재료가 얼마나 들어가는지.

| 필드 | 타입 | 예시 | 필수 |
|------|------|------|------|
| id | SERIAL (PK) | `200` | O |
| recipe_id | INT FK → recipes | `42` | O |
| ingredient_id | INT FK → ingredients | `7` | O |
| amount | VARCHAR(50) | `200` | X |
| unit | VARCHAR(20) | `g` | X |
| note | VARCHAR(100) | `채썰기` | X |
| sort_order | SMALLINT | `1` | O |

**제약**: `UNIQUE(recipe_id, ingredient_id)`

---

### tags (태그 사전)
레시피에 붙이는 분류 태그. 7개 카테고리로 관리.

| 필드 | 타입 | 예시 | 필수 |
|------|------|------|------|
| id | SERIAL (PK) | `5` | O |
| name | VARCHAR(50) | `볶음` | O |
| category | VARCHAR(20) | `method` | X |

**카테고리 목록**: `cuisine`(요리종류) / `protein`(단백질) / `carb`(탄수화물) / `method`(조리법) / `ingredient`(주재료) / `situation`(상황) / `source`(출처)

---

### recipe_tags (레시피-태그 연결)
M:N 관계 접합 테이블.

| 필드 | 타입 | 필수 |
|------|------|------|
| recipe_id | INT FK → recipes (PK) | O |
| tag_id | INT FK → tags (PK) | O |

---

### cook_logs (요리 이력) ★ 신규
"요리했어요" 버튼을 누를 때마다 기록. `cooked_count`의 상세 이력.

| 필드 | 타입 | 예시 | 필수 |
|------|------|------|------|
| id | SERIAL (PK) | `300` | O |
| recipe_id | INT FK → recipes | `42` | O |
| user_id | UUID FK → users | `a1b2c3d4-...` | O |
| cooked_at | TIMESTAMPTZ | `2026-03-19T18:30:00Z` | O |
| rating | SMALLINT (1-5) | `4` | X (Phase 3) |
| memo | TEXT | `다음엔 간장 반만` | X (Phase 3) |

---

### shopping_items (장보기 리스트) — Phase 2

| 필드 | 타입 | 예시 | 필수 |
|------|------|------|------|
| id | SERIAL (PK) | `500` | O |
| user_id | UUID FK → users | `a1b2c3d4-...` | O |
| name | VARCHAR(200) | `소고기 200g` | O |
| is_checked | BOOLEAN | `false` | O |
| created_at | TIMESTAMPTZ | `2026-03-19T...` | O |

---

## 인덱스 전략

```sql
-- 핵심 검색 성능
CREATE INDEX idx_recipes_user ON recipes(user_id, created_at DESC);
CREATE INDEX idx_recipes_cooked ON recipes(user_id, cooked_count DESC);
CREATE INDEX idx_recipe_tags_recipe ON recipe_tags(recipe_id);
CREATE INDEX idx_recipe_tags_tag ON recipe_tags(tag_id);
CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_ingredients_ingredient ON recipe_ingredients(ingredient_id);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_ingredients_name_en ON ingredients(name_en);
CREATE INDEX idx_cook_logs_recipe ON cook_logs(recipe_id);
```

---

## 왜 이 구조인가

**JSON 컬럼 제거 이유**:
- 기존: `tags_json`, `ingredients_json`, `steps_json` TEXT 컬럼에 JSON 문자열 저장
- 문제: 검색 시 `LIKE '%소고기%'` 방식으로 쿼리해야 하고, 정규화 테이블과 이중 조회 발생
- 해결: 모든 데이터를 정규화 테이블로 이동. 조인으로 정확한 쿼리 가능

**확장성**:
- Phase 2: `shopping_items` 테이블 추가만으로 장보기 기능 완성
- Phase 3: `cook_logs`에 `rating`, `memo` 컬럼이 이미 있음 (NULL로 대기)
- 모바일 앱 추가 시 API만 붙이면 됨 (DB 변경 없음)

---

## [NEEDS CLARIFICATION]

- [ ] Supabase Auth 사용 시 `users` 테이블을 Supabase 내장 테이블로 쓸지, 별도 `profiles` 테이블로 분리할지
- [ ] `ingredients` 시드 데이터: 기존 `ingredient_mapping.py`의 50+ 영한 매핑 데이터 마이그레이션 여부
