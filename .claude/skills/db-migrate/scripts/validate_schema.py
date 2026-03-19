#!/usr/bin/env python3
"""
NyamNyamBook v2 DB 스키마 변경 검증 스크립트
- JSON 컬럼 사용 여부 자동 감지
- Supabase RLS 영향 테이블 확인
- DO NOT 규칙 위반 사전 차단
"""
import sys
import re
import json
import argparse
from pathlib import Path


# JSON 컬럼 금지 패턴
JSON_COLUMN_PATTERNS = [
    (r"Column\(JSON\b", "JSON 타입 컬럼 사용"),
    (r"Column\(JSONB\b", "JSONB 타입 컬럼 사용"),
    (r"\w+_json\s*=\s*Column", "_json 접미사 컬럼 (JSON 저장 의심)"),
    (r"Column\(Text.*#.*json", "TEXT 컬럼에 JSON 저장 주석 감지"),
]

# Alembic 우회 패턴
ALEMBIC_BYPASS_PATTERNS = [
    (r"Base\.metadata\.create_all", "Base.metadata.create_all() 직접 호출"),
    (r"\bdb\.create_all\b", "db.create_all() 직접 호출"),
    (r"engine\.execute\(schema\.CreateTable", "engine.execute(CreateTable) 직접 호출"),
]

# RLS가 필요한 테이블 (사용자 데이터가 있는 테이블)
TABLES_REQUIRING_RLS = {
    "recipes", "recipe_ingredients", "recipe_steps", "recipe_tags",
    "cook_logs", "shopping_list_items"
}


def check_model_file(filepath: str) -> list[dict]:
    """SQLAlchemy 모델 파일에서 위반 사항 검사."""
    path = Path(filepath)
    if not path.exists():
        return [{"type": "ERROR", "message": f"파일을 찾을 수 없습니다: {filepath}"}]

    content = path.read_text(encoding='utf-8', errors='replace')
    lines = content.splitlines()
    violations = []

    for i, line in enumerate(lines, 1):
        # JSON 컬럼 검사
        for pattern, description in JSON_COLUMN_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append({
                    "type": "ERROR",
                    "rule": "json_column",
                    "line": i,
                    "content": line.strip(),
                    "message": f"JSON 컬럼 금지: {description}",
                    "fix": "정규화 테이블(recipe_tags, recipe_ingredients, recipe_steps)을 사용하세요.",
                })

        # Alembic 우회 검사
        for pattern, description in ALEMBIC_BYPASS_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append({
                    "type": "ERROR",
                    "rule": "alembic_bypass",
                    "line": i,
                    "content": line.strip(),
                    "message": f"Alembic 우회 금지: {description}",
                    "fix": "alembic revision --autogenerate 후 alembic upgrade head를 사용하세요.",
                })

    return violations


def check_migration_file(filepath: str) -> list[dict]:
    """Alembic revision 파일 검사."""
    path = Path(filepath)
    if not path.exists():
        return [{"type": "ERROR", "message": f"파일을 찾을 수 없습니다: {filepath}"}]

    content = path.read_text(encoding='utf-8', errors='replace')
    violations = []

    # JSON 컬럼 검사
    for i, line in enumerate(content.splitlines(), 1):
        for pattern, description in JSON_COLUMN_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append({
                    "type": "ERROR",
                    "rule": "json_column",
                    "line": i,
                    "content": line.strip(),
                    "message": f"마이그레이션에 JSON 컬럼 감지: {description}",
                    "fix": "정규화 테이블로 대체하세요.",
                })

    # RLS 누락 확인 (새 테이블 생성 시)
    new_tables = re.findall(r"op\.create_table\(['\"](\w+)['\"]", content)
    for table in new_tables:
        if table in TABLES_REQUIRING_RLS:
            if "ENABLE ROW LEVEL SECURITY" not in content:
                violations.append({
                    "type": "WARNING",
                    "rule": "rls_missing",
                    "line": None,
                    "message": f"테이블 '{table}'에 RLS 활성화 누락",
                    "fix": "upgrade() 함수에 다음을 추가하세요:\nop.execute('ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')".format(table=table),
                })

    # downgrade() 함수 존재 확인
    if "def downgrade" not in content:
        violations.append({
            "type": "WARNING",
            "rule": "no_downgrade",
            "message": "downgrade() 함수가 없습니다.",
            "fix": "롤백을 위한 downgrade() 함수를 추가하세요.",
        })

    return violations


def main():
    parser = argparse.ArgumentParser(description="NyamNyamBook v2 DB 스키마 변경 검증")
    parser.add_argument("filepath", help="검사할 파일 경로 (모델 파일 또는 Alembic revision 파일)")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
    args = parser.parse_args()

    filepath = args.filepath

    # 파일 타입 자동 감지
    if "versions" in filepath or "migration" in filepath.lower():
        violations = check_migration_file(filepath)
        file_type = "Alembic Revision"
    else:
        violations = check_model_file(filepath)
        file_type = "SQLAlchemy 모델"

    if args.json:
        print(json.dumps({
            "file": filepath,
            "type": file_type,
            "violations": violations,
            "passed": len([v for v in violations if v["type"] == "ERROR"]) == 0,
        }, ensure_ascii=False, indent=2))
        return

    print(f"\n스키마 변경 검증: {filepath} ({file_type})")
    print("=" * 55)

    if not violations:
        print("✅ 모든 규칙 통과! DB 변경을 적용해도 됩니다.\n")
        sys.exit(0)

    errors = [v for v in violations if v["type"] == "ERROR"]
    warnings = [v for v in violations if v["type"] == "WARNING"]

    if errors:
        print(f"\n❌ 오류 {len(errors)}개 (DB 변경 차단):")
        for v in errors:
            loc = f" (Line {v['line']})" if v.get("line") else ""
            print(f"\n  [{v['rule']}]{loc}")
            if v.get("content"):
                print(f"  코드: {v['content']}")
            print(f"  문제: {v['message']}")
            print(f"  조치: {v['fix']}")

    if warnings:
        print(f"\n⚠️  경고 {len(warnings)}개 (확인 후 진행 가능):")
        for v in warnings:
            print(f"\n  [{v['rule']}]")
            print(f"  문제: {v['message']}")
            print(f"  조치: {v['fix']}")

    if errors:
        print(f"\n→ {len(errors)}개 오류를 수정 후 다시 실행하세요.\n")
        sys.exit(1)
    else:
        print(f"\n→ 경고 확인 후 DB 변경을 진행하세요.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
