# Alembic 자주 쓰는 패턴

## 1. 기본 명령어 순서

```bash
cd backend

# 1. 모델 파일 수정 후
alembic revision --autogenerate -m "add_rating_to_cook_logs"

# 2. 생성된 파일 확인 (alembic/versions/ 폴더)
# 3. 내용이 맞으면 적용
alembic upgrade head

# 현재 상태 확인
alembic current

# 이전으로 되돌리기 (문제 발생 시)
alembic downgrade -1
```

## 2. 컬럼 추가

```python
def upgrade() -> None:
    op.add_column('recipes', sa.Column('cook_time', sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_column('recipes', 'cook_time')
```

## 3. 컬럼 타입 변경 (데이터 손실 주의)

```python
def upgrade() -> None:
    # 문자열 → 정수 변환 (데이터 보존)
    op.add_column('recipes', sa.Column('total_time_new', sa.Integer(), nullable=True))
    op.execute("UPDATE recipes SET total_time_new = CAST(NULLIF(total_time, '') AS INTEGER)")
    op.drop_column('recipes', 'total_time')
    op.alter_column('recipes', 'total_time_new', new_column_name='total_time')

def downgrade() -> None:
    op.alter_column('recipes', 'total_time', type_=sa.String(50))
```

## 4. 인덱스 추가 (10개 인덱스 전략)

```python
def upgrade() -> None:
    # 단일 컬럼 인덱스
    op.create_index('ix_recipes_user_id', 'recipes', ['user_id'])

    # 복합 인덱스 (검색 최적화)
    op.create_index('ix_recipes_user_created', 'recipes', ['user_id', 'created_at'])

    # 부분 인덱스 (공개 레시피만)
    op.create_index(
        'ix_recipes_public',
        'recipes',
        ['created_at'],
        postgresql_where=sa.text('is_public = true')
    )

def downgrade() -> None:
    op.drop_index('ix_recipes_public')
    op.drop_index('ix_recipes_user_created')
    op.drop_index('ix_recipes_user_id')
```

## 5. 외래키 추가

```python
def upgrade() -> None:
    op.add_column('recipe_tags',
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id'), nullable=False)
    )

def downgrade() -> None:
    op.drop_column('recipe_tags', 'tag_id')
```

## 6. NOT NULL 컬럼 추가 (기존 데이터 있을 때)

```python
def upgrade() -> None:
    # 1. nullable로 먼저 추가
    op.add_column('recipes', sa.Column('source_type', sa.String(20), nullable=True))

    # 2. 기존 데이터에 기본값 채우기
    op.execute("UPDATE recipes SET source_type = 'manual' WHERE source_type IS NULL")

    # 3. NOT NULL로 변경
    op.alter_column('recipes', 'source_type', nullable=False)

def downgrade() -> None:
    op.drop_column('recipes', 'source_type')
```

## 7. 테이블 신규 생성 (정규화 테이블)

```python
def upgrade() -> None:
    op.create_table(
        'shopping_list_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('ingredient_name', sa.String(200), nullable=False),
        sa.Column('amount', sa.String(100), nullable=True),
        sa.Column('is_checked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_shopping_list_user_id', 'shopping_list_items', ['user_id'])

def downgrade() -> None:
    op.drop_index('ix_shopping_list_user_id')
    op.drop_table('shopping_list_items')
```

## 8. Supabase RLS 정책 (마이그레이션에서 처리)

```python
def upgrade() -> None:
    op.create_table('shopping_list_items', ...)

    # RLS 활성화 (항상 포함)
    op.execute("ALTER TABLE shopping_list_items ENABLE ROW LEVEL SECURITY")

    # 본인 데이터만 접근 정책
    op.execute("""
        CREATE POLICY "Users can manage own shopping list"
        ON shopping_list_items
        FOR ALL
        USING (auth.uid()::text = user_id)
        WITH CHECK (auth.uid()::text = user_id)
    """)

def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS \"Users can manage own shopping list\" ON shopping_list_items")
    op.drop_table('shopping_list_items')
```

## 9. 문제 해결: Alembic 히스토리 불일치

DB와 Alembic 히스토리가 맞지 않을 때:
```bash
# 현재 DB 상태를 Alembic 최신으로 강제 표시 (주의: 실제 스키마 변경 없음)
alembic stamp head

# 이후 alembic check로 정상 확인
alembic check
```

이 명령은 `db.create_all()`로 스키마를 직접 생성했을 때 복구용으로만 사용한다.
