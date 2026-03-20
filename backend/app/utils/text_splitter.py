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


def split_youtube_description(full_text: str) -> tuple[list[str], list[str]]:
    """
    YouTube description 텍스트에서 재료/조리단계를 추출한다.
    기존 intelligent_text_splitter 로직 이식.
    returns: (ingredients, steps)
    """
    if not full_text:
        return [], []

    GARBAGE = {
        'http', 'www', '.com', '구독', '좋아요', 'instagram', 'business',
        '문의', 'song by', 'music', 'rights reserved', 'copyright', 'bgm',
        '브금', '출처', 'link', 'follow', 'thanks to', '협찬', '광고',
        '비즈니스', 'timestamps', 'affiliate', 'tools', 'connect:',
        'fan mail:', 'website:', 'recipe below', 'print recipe',
    }
    ing_header = re.compile(
        r'ingredient|재료|양념|sauce|prep|what.*need', re.IGNORECASE
    )
    step_header = re.compile(
        r'step|direction|instruction|만드|조리|how.*make|procedure|cook|timestamps',
        re.IGNORECASE,
    )
    ing_pattern = re.compile(
        r'[가-힣a-zA-Z]+.*\d+|[가-힣a-zA-Z]+.*'
        r'(?:큰술|작은술|컵|개|마리|g|kg|ml|L|꼬집|주먹|T|t|스푼|알|장|줌)'
    )
    step_start = re.compile(r'^(\d+[\.\)]\s*|step\s*\d+)', re.IGNORECASE)
    timestamp = re.compile(r'^\d{1,2}:\d{2}\s*[-–—]')

    # 첫 번째 섹션 헤더 이전 인트로는 제거
    lines_raw = full_text.split('\n')
    first_header_idx = 0
    for idx, ln in enumerate(lines_raw):
        ln_stripped = ln.strip()
        if not ln_stripped:
            continue
        if (ing_header.search(ln_stripped) or step_header.search(ln_stripped)) and len(ln_stripped) < 40:
            first_header_idx = idx
            break
    lines_raw = lines_raw[first_header_idx:]

    ingredients: list[str] = []
    steps: list[str] = []
    mode = 0  # 0=unknown 1=ingredients 2=steps
    last_was_ing = False

    for line in lines_raw:
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if any(bad in lower for bad in GARBAGE):
            continue
        if timestamp.match(line):
            continue

        # 헤더 감지: 콜론 있거나 / 짧은 라인에 키워드만 있는 경우 ([ 재료 ], 재료: 등)
        is_short = len(line) < 40
        if ing_header.search(line) and (is_short or ':' in line):
            mode = 1
            last_was_ing = True
            continue
        if step_header.search(line) and (is_short or ':' in line):
            mode = 2
            last_was_ing = False
            continue

        clean = re.sub(r'^[►▪•\-\*\s]+', '', line).strip()
        if not clean or len(clean) < 3:
            continue

        if mode == 1:
            if len(line) < 120 and not step_start.match(line):
                if clean not in ingredients:
                    ingredients.append(clean)
            elif step_start.match(line):
                mode = 2
                last_was_ing = False
                steps.append(line)
        elif mode == 2:
            steps.append(line)
        else:
            if step_start.match(line):
                steps.append(line)
                mode = 2
                last_was_ing = False
            elif len(line) < 80 and ing_pattern.search(line):
                if clean not in ingredients:
                    ingredients.append(clean)
                last_was_ing = True
            elif last_was_ing and len(line) < 120 and not step_start.match(line):
                if clean not in ingredients:
                    ingredients.append(clean)
            elif len(line) > 20:
                steps.append(line)
                last_was_ing = False

    return ingredients, steps


def normalize_string(text: str) -> str:
    """HTML 태그 제거, 공백 정규화"""
    import html
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ").replace("\u200b", "").replace("\r\n", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()
