from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str
    name_en: str | None = None


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int

    model_config = {"from_attributes": True}


class RecipeIngredientIn(BaseModel):
    """레시피에 재료를 연결할 때 사용하는 입력 스키마"""
    name: str           # 재료명 (없으면 자동 생성)
    amount: str | None = None
    unit: str | None = None
    note: str | None = None
    sort_order: int = 0


class RecipeIngredientResponse(BaseModel):
    id: int
    ingredient: IngredientResponse
    amount: str | None
    unit: str | None
    note: str | None
    sort_order: int

    model_config = {"from_attributes": True}
