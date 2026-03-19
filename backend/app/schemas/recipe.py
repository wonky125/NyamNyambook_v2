import uuid
from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator

from app.schemas.ingredient import RecipeIngredientIn, RecipeIngredientResponse
from app.schemas.tag import TagResponse


class RecipeStepIn(BaseModel):
    step_number: int
    instruction: str
    image_url: str | None = None


class RecipeStepResponse(BaseModel):
    id: int
    step_number: int
    instruction: str
    image_url: str | None

    model_config = {"from_attributes": True}


class RecipeCreate(BaseModel):
    title: str
    description: str | None = None
    servings: str | None = None
    prep_time: int | None = None
    cook_time: int | None = None
    total_time: int | None = None
    image_url: str | None = None
    source_url: str | None = None
    source_type: str | None = None
    notes: str | None = None
    steps: list[RecipeStepIn] = []
    ingredients: list[RecipeIngredientIn] = []
    tag_ids: list[int] = []


class RecipeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    servings: str | None = None
    prep_time: int | None = None
    cook_time: int | None = None
    total_time: int | None = None
    image_url: str | None = None
    source_url: str | None = None
    notes: str | None = None
    steps: list[RecipeStepIn] | None = None
    ingredients: list[RecipeIngredientIn] | None = None
    tag_ids: list[int] | None = None


class RecipeSummary(BaseModel):
    """목록 조회용 — 상세 데이터 제외"""
    id: int
    title: str
    description: str | None
    servings: str | None
    total_time: int | None
    image_url: str | None
    source_type: str | None
    cooked_count: int
    created_at: datetime
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tags(cls, v):
        if v and hasattr(v[0], "tag"):
            return [rt.tag for rt in v]
        return v


class RecipeDetail(RecipeSummary):
    """상세 조회용"""
    source_url: str | None
    notes: str | None
    prep_time: int | None
    cook_time: int | None
    updated_at: datetime
    steps: list[RecipeStepResponse] = []
    ingredients: list[RecipeIngredientResponse] = []
