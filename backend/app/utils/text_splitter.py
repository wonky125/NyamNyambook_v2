"""재료 문자열을 (이름, 양, 단위, 메모)로 파싱하는 유틸"""
import re

UNITS = [
    "kg", "g", "ml", "l", "L", "컵", "큰술", "작은술", "T", "t",
    "개", "장", "마리", "봉지", "팩", "캔", "병", "줌", "꼬집",
    "인분", "조각", "쪽", "알", "줄기", "대", "뿌리", "장", "토막",
    "cc", "oz", "lb", "tbsp", "tsp", "cup",
]

UNIT_PATTERN = re.compile(
    r"(\d+(?:[./]\d+)?(?:\.\d+)?)\s*(" + "|".join(re.escape(u) for u in UNITS) + r")\b",
    re.IGNORECASE,
)


def parse_ingredient_line(line: str) -> dict:
    """
    '소고기 200g (채썰기)' → {name, amount, unit, note}
    """
    line = line.strip()
    note = None

    # 괄호 안 메모 추출
    note_match = re.search(r"\(([^)]+)\)", line)
    if note_match:
        note = note_match.group(1).strip()
        line = line[: note_match.start()].strip()

    # 양 + 단위 추출
    amount = None
    unit = None
    unit_match = UNIT_PATTERN.search(line)
    if unit_match:
        amount = unit_match.group(1)
        unit = unit_match.group(2)
        name = (line[: unit_match.start()] + line[unit_match.end():]).strip()
    else:
        # 숫자만 있는 경우
        num_match = re.search(r"(\d+(?:[./]\d+)?)", line)
        if num_match:
            amount = num_match.group(1)
            name = (line[: num_match.start()] + line[num_match.end():]).strip()
        else:
            name = line

    return {"name": name or line, "amount": amount, "unit": unit, "note": note}


def normalize_string(text: str) -> str:
    """HTML 태그 제거, 공백 정규화"""
    import html
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ").replace("\u200b", "").replace("\r\n", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()
