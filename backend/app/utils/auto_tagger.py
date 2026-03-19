"""레시피 제목/재료 기반 자동 태그 추천"""

TAG_RULES: list[tuple[str, list[str], str]] = [
    # (태그명, 트리거 키워드, 카테고리)
    # --- 단백질 ---
    ("소고기", ["소고기", "불고기", "갈비", "beef", "ribeye"], "protein"),
    ("돼지고기", ["돼지", "삼겹", "목살", "pork"], "protein"),
    ("닭고기", ["닭", "chicken", "치킨"], "protein"),
    ("해산물", ["새우", "오징어", "조개", "고등어", "연어", "참치", "shrimp", "fish"], "protein"),
    ("두부", ["두부", "tofu"], "protein"),
    ("달걀", ["달걀", "계란", "egg"], "protein"),
    # --- 탄수화물 ---
    ("밥", ["볶음밥", "비빔밥", "덮밥", "김밥", "주먹밥", "밥"], "carb"),
    ("면", ["라면", "우동", "파스타", "국수", "냉면", "소면", "면"], "carb"),
    ("빵", ["빵", "토스트", "샌드위치", "bread", "toast"], "carb"),
    # --- 조리법 ---
    ("볶음", ["볶음", "볶기", "炒", "stir fry", "stir-fry"], "method"),
    ("끓이기", ["국", "찌개", "탕", "끓이", "soup", "stew"], "method"),
    ("구이", ["구이", "굽기", "grilled", "baked", "roast"], "method"),
    ("찜", ["찜", "steam"], "method"),
    ("튀김", ["튀김", "전", "부침", "fry", "fried"], "method"),
    ("무침", ["무침", "나물", "샐러드", "salad"], "method"),
    # --- 상황 ---
    ("간단", ["10분", "5분", "간단", "easy", "quick", "빠른"], "situation"),
    ("야식", ["야식", "야간", "night"], "situation"),
    ("다이어트", ["다이어트", "저칼로리", "diet", "low calorie"], "situation"),
    ("술안주", ["안주", "맥주", "소주", "snack"], "situation"),
    # --- 요리 종류 ---
    ("한식", ["된장", "고추장", "간장게장", "김치", "한식", "Korean"], "cuisine"),
    ("일식", ["스시", "라멘", "우동", "돈까스", "Japanese"], "cuisine"),
    ("중식", ["짜장", "짬뽕", "탕수육", "Chinese"], "cuisine"),
    ("양식", ["파스타", "피자", "스테이크", "Western", "Italian"], "cuisine"),
]


def suggest_tags(title: str, ingredient_names: list[str]) -> list[str]:
    """제목 + 재료 이름 기반으로 태그명 목록 반환"""
    combined = (title + " " + " ".join(ingredient_names)).lower()
    matched: list[str] = []
    seen: set[str] = set()

    for tag_name, keywords, _category in TAG_RULES:
        if tag_name in seen:
            continue
        for kw in keywords:
            if kw.lower() in combined:
                matched.append(tag_name)
                seen.add(tag_name)
                break

    return matched
