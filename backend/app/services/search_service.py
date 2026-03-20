"""레시피 검색 — 제목 + 재료명 ILIKE"""
import uuid

from sqlalchemy import select, desc, or_
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe
from app.models.ingredient import Ingredient, RecipeIngredient
from app.models.tag import RecipeTag


async def search_recipes(
    db: AsyncSession,
    user_id: str,
    query: str,
    page: int = 1,
    per_page: int = 20,
) -> list[Recipe]:
    keyword = f"%{query}%"

    # 재료명으로 매칭되는 recipe_id 목록
    ingredient_subq = (
        select(RecipeIngredient.recipe_id)
        .join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id)
        .where(or_(Ingredient.name.ilike(keyword), Ingredient.name_en.ilike(keyword)))
    )

    from app.models.recipe import RecipeStep
    from app.models.ingredient import RecipeIngredient as RI

    stmt = (
        select(Recipe)
        .options(
            selectinload(Recipe.recipe_tags).selectinload(RecipeTag.tag),
            selectinload(Recipe.recipe_ingredients).selectinload(RI.ingredient),
            selectinload(Recipe.steps),
        )
        .where(
            Recipe.user_id == uuid.UUID(user_id),
            or_(
                Recipe.title.ilike(keyword),
                Recipe.id.in_(ingredient_subq),
            ),
        )
        .order_by(desc(Recipe.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    result = await db.execute(stmt)
    return list(result.scalars().unique().all())
