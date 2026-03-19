---
name: db-migrate
description: This skill should be used when the user asks to change, add, or modify database schema — including "테이블 추가해줘", "컬럼 바꿔줘", "DB 수정해줘", "DB 스키마 변경", "마이그레이션해줘", "migrate", "새 모델 추가", "컬럼 추가", "필드 추가", "테이블 만들어줘". Use this skill whenever any database schema change is needed — even if the user doesn't say "migration" explicitly. This skill enforces NyamNyamBook v2 DO NOT rules: always shows a plan first, always uses Alembic (never db.create_all()), always blocks JSON columns, and requires explicit user approval before applying changes to the database.
---

# db-migrate

> DB 스키마 변경을 Alembic으로 안전하게 실행합니다. 계획 먼저, 승인 후 실행 — PRD "변경 전 계획 보여주기" 규칙을 스킬 구조로 강제합니다.

## 워크플로우

### Step 1: 변경 의도 파악 (prompt)

Read the user's change request and `PRD/02_DATA_MODEL.md` to understand the current schema.

Extract from the request:
- 변경 대상 테이블명
- 추가/수정/삭제할 컬럼명과 타입
- 변경 이유 (기능 추가, 버그 수정, 최적화 등)
- Phase 범위 확인 (`PRD/03_PHASES.md` 참조 — Phase 2/3 범위 변경은 경고)

변경 계획을 표로 출력 (이 단계를 절대 생략하지 않는다):

```
DB 변경 계획

테이블: cook_logs
변경 유형: 컬럼 추가

| 컬럼명  | 타입         | NOT NULL | 기본값 | 설명          |
|---------|--------------|----------|--------|---------------|
| rating  | SMALLINT     | NO       | NULL   | 별점 (1-5)    |
| memo    | TEXT         | NO       | NULL   | 요리 후 메모  |

영향 범위:
- 모델 파일: app/models/cook_log.py
- 스키마 파일: app/schemas/cook_log.py
- Alembic revision: 신규 생성 필요
- RLS 정책: 변경 없음 (기존 정책 유지)
```

### Step 2: DO NOT 규칙 검사 (review)

Before writing any code, validate the change against project rules:

**자동 차단 항목 (발견 시 즉시 중단):**
- JSON 컬럼 요청: `Column(JSON)`, `Column(JSONB)`, `Column(Text)` + JSON 저장 패턴
  → 거부 메시지: "JSON 컬럼은 이 프로젝트에서 금지입니다. 대신 정규화 테이블을 사용하세요."
  → 대안 제시: 어떤 정규화 테이블 구조가 적합한지 설계해서 보여준다.

- `db.create_all()` 또는 `Base.metadata.create_all()` 사용 요청
  → 거부 메시지: "직접 create_all()은 금지입니다. Alembic 마이그레이션을 생성할게요."

**경고 항목 (사용자에게 알리고 계속):**
- Phase 2/3 기능 추가 감지 (예: YouTube 스크래퍼 관련 테이블)
  → 경고: "이 변경은 PRD Phase 2 범위입니다. 계속 진행할까요?"
- 기존 컬럼 타입 변경 (데이터 손실 위험)
  → 경고: "기존 데이터가 있으면 변환이 필요합니다. Alembic에 데이터 변환 로직을 추가할게요."
- NOT NULL 컬럼 추가 (기존 행이 있으면 기본값 필요)
  → 경고: "기존 데이터에 기본값을 지정해야 합니다. 기본값을 알려주세요."

### Step 3: 코드 생성 (generate)

Generate the necessary code changes. Print each file's content before writing.

**SQLAlchemy 모델 변경** (`app/models/{table}.py`):
```python
# 추가되는 컬럼 예시
from sqlalchemy import Column, SmallInteger, Text

class CookLog(Base):
    __tablename__ = "cook_logs"
    # 기존 컬럼들...
    rating = Column(SmallInteger, nullable=True)  # 별점 1-5
    memo = Column(Text, nullable=True)             # 요리 후 메모
```

**Pydantic 스키마 변경** (`app/schemas/{table}.py`):
```python
class CookLogCreate(BaseModel):
    recipe_id: int
    rating: int | None = None  # 1-5
    memo: str | None = None

class CookLogResponse(BaseModel):
    id: int
    recipe_id: int
    rating: int | None
    memo: str | None
    cooked_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Alembic revision 파일** (내용만 보여주고, 실제 생성은 Step 4 이후):
```python
# alembic/versions/XXXX_{description}.py
def upgrade() -> None:
    op.add_column('cook_logs', sa.Column('rating', sa.SmallInteger(), nullable=True))
    op.add_column('cook_logs', sa.Column('memo', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('cook_logs', 'memo')
    op.drop_column('cook_logs', 'rating')
```

데이터 변환이 필요한 경우 `upgrade()` 내에 Python 로직을 포함한다:
```python
def upgrade() -> None:
    op.add_column('recipes', sa.Column('total_time_int', sa.Integer(), nullable=True))
    # 기존 문자열 데이터를 정수로 변환
    op.execute("UPDATE recipes SET total_time_int = CAST(total_time AS INTEGER) WHERE total_time ~ '^[0-9]+$'")
    op.drop_column('recipes', 'total_time')
    op.alter_column('recipes', 'total_time_int', new_column_name='total_time')
```

### Step 4: 사용자 승인 게이트 (review) ← 절대 생략 금지

Show the complete plan and generated code. Wait for explicit approval before any database changes.

```
최종 확인: 아래 변경을 DB에 적용할까요?

변경 내용:
- cook_logs.rating (SMALLINT, nullable)
- cook_logs.memo (TEXT, nullable)

생성될 파일:
- app/models/cook_log.py (수정)
- app/schemas/cook_log.py (수정)
- alembic/versions/{revision_id}_add_rating_memo_to_cook_logs.py (신규)

실행될 명령어:
alembic upgrade head

[Y] 승인하고 적용  [N] 취소
```

Pause and wait for user confirmation. Do not execute `alembic upgrade head` without explicit approval.

### Step 5: 실행 및 검증 (script)

After user approves, execute in sequence:

```bash
# 1. 모델 파일 수정
# (Step 3에서 생성한 코드를 실제 파일에 적용)

# 2. Alembic revision 생성
cd backend
alembic revision --autogenerate -m "{description}"

# 3. 생성된 파일 내용 확인 (자동 생성이 의도와 맞는지)
# → Step 3의 초안과 비교하여 차이가 있으면 사용자에게 알림

# 4. DB에 적용
alembic upgrade head

# 5. 적용 결과 확인
alembic current
```

Print final result:
```
마이그레이션 완료!

적용된 revision: {revision_id}
변경된 테이블: cook_logs
추가된 컬럼: rating, memo

현재 DB 상태: alembic current → {revision_id} (head)

다음 단계:
- pytest tests/ 로 기존 테스트가 깨지지 않는지 확인
- FastAPI /docs 에서 새 필드가 스키마에 반영됐는지 확인
```

## References
- **`references/alembic-patterns.md`** — Alembic 자주 쓰는 패턴 (컬럼 추가, 인덱스, 외래키, 데이터 변환)

## Scripts
- **`scripts/validate_schema.py`** — JSON 컬럼 사용 여부 + RLS 정책 영향 자동 검사

## Settings
| 설정 | 기본값 | 변경 방법 |
|------|--------|-----------|
| Alembic 경로 | `backend/` | 프로젝트 루트에서 실행 시 `cd backend` 먼저 |
| autogenerate 사용 | 항상 사용 | Step 5에서 수동 수정 가능 |
| 승인 게이트 | 항상 필수 | 생략 불가 — PRD 규칙 |
