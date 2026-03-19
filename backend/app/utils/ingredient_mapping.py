"""재료 영한 매핑 — ingredients 테이블 시드 데이터"""

INGREDIENT_EN_KO: dict[str, str] = {
    "beef": "소고기",
    "pork": "돼지고기",
    "chicken": "닭고기",
    "shrimp": "새우",
    "tofu": "두부",
    "egg": "달걀",
    "eggs": "달걀",
    "rice": "쌀",
    "noodle": "면",
    "noodles": "면",
    "onion": "양파",
    "garlic": "마늘",
    "ginger": "생강",
    "carrot": "당근",
    "potato": "감자",
    "sweet potato": "고구마",
    "spinach": "시금치",
    "cabbage": "양배추",
    "mushroom": "버섯",
    "mushrooms": "버섯",
    "soy sauce": "간장",
    "sesame oil": "참기름",
    "sugar": "설탕",
    "salt": "소금",
    "pepper": "후추",
    "red pepper paste": "고추장",
    "soybean paste": "된장",
    "oil": "식용유",
    "butter": "버터",
    "flour": "밀가루",
    "milk": "우유",
    "cheese": "치즈",
    "water": "물",
    "green onion": "파",
    "scallion": "실파",
    "zucchini": "애호박",
    "cucumber": "오이",
    "tomato": "토마토",
    "lemon": "레몬",
    "vinegar": "식초",
    "corn starch": "전분",
    "oyster sauce": "굴소스",
    "fish sauce": "액젓",
    "sesame seeds": "깨",
    "seaweed": "김",
    "anchovy": "멸치",
    "tuna": "참치",
    "spam": "스팸",
}

# 역방향 (한→영)
INGREDIENT_KO_EN: dict[str, str] = {v: k for k, v in INGREDIENT_EN_KO.items()}


def get_english_name(korean_name: str) -> str | None:
    return INGREDIENT_KO_EN.get(korean_name)


def get_korean_name(english_name: str) -> str | None:
    return INGREDIENT_EN_KO.get(english_name.lower())
