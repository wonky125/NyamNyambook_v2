#!/usr/bin/env python3
"""
NyamNyamBook v2 DO NOT 규칙 위반 정적 스캔
PRD의 "절대 하지 마" 목록을 코드에서 자동 감지합니다.
"""
import sys
import re
import json
from pathlib import Path


RULES = [
    {
        "id": "json_column",
        "name": "JSON 컬럼 사용 금지",
        "patterns": [
            r"Column\(JSON",
            r"Column\(JSONB",
            r"\w+_json\s*=\s*Column",
            r"json\.dumps.*Column",
        ],
        "severity": "ERROR",
        "message": "JSON 컬럼 대신 정규화 테이블(recipe_tags, recipe_ingredients, recipe_steps)을 사용하세요.",
    },
    {
        "id": "env_hardcoded",
        "name": "환경변수 하드코딩 금지",
        "patterns": [
            r'(SUPABASE|DATABASE|JWT|SECRET|API_KEY|PASSWORD)\s*=\s*["\'][^"\']{8,}["\']',
            r'eyJ[A-Za-z0-9_-]{20,}',  # JWT token pattern
            r'postgresql://[^{]',        # DB URL with credentials
        ],
        "severity": "ERROR",
        "message": ".env 파일과 app/config.py의 Settings 클래스를 사용하세요. 코드에 직접 값을 넣지 마세요.",
    },
    {
        "id": "db_create_all",
        "name": "db.create_all() 직접 호출 금지",
        "patterns": [
            r"create_all\(",
            r"Base\.metadata\.create_all",
            r"db\.create_all",
        ],
        "severity": "ERROR",
        "message": "Alembic 마이그레이션을 사용하세요: alembic revision --autogenerate → alembic upgrade head",
    },
    {
        "id": "flask_auth_pattern",
        "name": "Flask 인증 패턴 사용 금지",
        "patterns": [
            r"@login_required",
            r"current_user\s*=\s*None",  # Flask-Login global
            r"from flask_login import",
            r"session\[.user_id.\]",
        ],
        "severity": "ERROR",
        "message": "FastAPI의 Depends(get_current_user) 패턴을 사용하세요.",
    },
    {
        "id": "no_ownership_check",
        "name": "소유권 검증 누락 (상태 변경 엔드포인트)",
        "patterns": [
            r"@router\.(post|put|delete|patch).*\n.*user_id.*Query",
            r"user_id:\s*int\s*=\s*Query",
        ],
        "severity": "WARNING",
        "message": "user_id를 쿼리 파라미터로 받는 대신 Depends(get_current_user)로 인증된 사용자 ID를 사용하세요.",
    },
    {
        "id": "rls_disable",
        "name": "Supabase RLS 비활성화 금지",
        "patterns": [
            r"DISABLE ROW LEVEL SECURITY",
            r"disable_rls",
            r"service_role.*flutter",  # service role key in frontend
        ],
        "severity": "ERROR",
        "message": "Supabase RLS를 비활성화하지 마세요. RLS 정책을 올바르게 설정하세요.",
    },
    {
        "id": "requests_sync",
        "name": "동기 requests 사용 (FastAPI에서 금지)",
        "patterns": [
            r"import requests\b",
            r"requests\.get\(",
            r"requests\.post\(",
            r"requests\.Session\(",
        ],
        "severity": "WARNING",
        "message": "FastAPI에서는 httpx.AsyncClient를 사용하세요. 동기 requests는 이벤트 루프를 블로킹합니다.",
    },
]


def scan_file(filepath: str) -> list[dict]:
    """파일을 스캔하여 규칙 위반을 반환합니다."""
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: 파일을 찾을 수 없습니다: {filepath}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding='utf-8', errors='replace')
    lines = content.splitlines()

    violations = []

    for rule in RULES:
        for pattern in rule["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "severity": rule["severity"],
                        "line_number": i,
                        "line_content": line.strip(),
                        "message": rule["message"],
                    })

    return violations


def main():
    if len(sys.argv) < 2:
        print("사용법: python check_rules.py <파일경로> [--json]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    output_json = "--json" in sys.argv

    violations = scan_file(filepath)

    if output_json:
        print(json.dumps(violations, ensure_ascii=False, indent=2))
        return

    errors = [v for v in violations if v["severity"] == "ERROR"]
    warnings = [v for v in violations if v["severity"] == "WARNING"]

    print(f"\nDO NOT 규칙 검사 결과: {filepath}")
    print("=" * 50)

    if not violations:
        print("✅ 모든 규칙 통과! 위반 사항 없음.\n")
        sys.exit(0)

    if errors:
        print(f"\n❌ ERROR {len(errors)}개:")
        for v in errors:
            print(f"  Line {v['line_number']}: [{v['rule_name']}]")
            print(f"    코드: {v['line_content']}")
            print(f"    조치: {v['message']}")
            print()

    if warnings:
        print(f"\n⚠️  WARNING {len(warnings)}개:")
        for v in warnings:
            print(f"  Line {v['line_number']}: [{v['rule_name']}]")
            print(f"    코드: {v['line_content']}")
            print(f"    조치: {v['message']}")
            print()

    print(f"총 {len(errors)}개 ERROR, {len(warnings)}개 WARNING 발견\n")

    if errors:
        sys.exit(1)  # ERROR가 있으면 비정상 종료 (포팅 중단)
    else:
        sys.exit(0)  # WARNING만 있으면 정상 종료 (포팅 계속)


if __name__ == "__main__":
    main()
