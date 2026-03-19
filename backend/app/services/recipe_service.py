"""레시피 CRUD 비즈니스 로직"""
import uuid

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recipe import Recipe
from app.models.recipe_step import RecipeStep
from app.models.ingredient import Ingredient, RecipeIngredient
from app.models.tag import Tag, RecipeTag
from app.schemas.recipe import RecipeCreate, RecipeUpdate


async def _get_or_create_ingredient(db: AsyncSession, name: str) -> Ingredient:
    result = await db.execute(select(Ingredient).where(Ingredient.name == name))
    ing = result.scalar_one_or_none()
    if not ing:
        from app.utils.ingredient_mapping import get_english_name
        ing = Ingredient(name=name, name_en=get_english_name(name))
        db.add(ing)
        await db.flush()
    return ing


def _recipe_query():
    return (
        select(Recipe)
        .options(
            selectinload(Recipe.steps),
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.recipe_tags).selectinload(RecipeTag.tag),
        )
    )


async def get_user_recipes(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    per_page: int = 20,
    tag_id: int | None = None,
    source_type: str | None = None,
) -> tuple[list[Recipe], int]:
    query = _recipe_query().where(Recipe.user_id == uuid.UUID(user_id))

    if tag_id:
        query = query.join(Recipe.recipe_tags).where(RecipeTag.tag_id == tag_id)
    if source_type:
        query = query.where(Recipe.source_type == source_type)

    query = query.order_by(desc(Recipe.created_at))

    count_q = select(func.count(Recipe.id)).where(Recipe.user_id == uuid.UUID(user_id))
    if tag_id:
        count_q = count_q.join(Recipe.recipe_tags).where(RecipeTag.tag_id == tag_id)
    if source_type:
        count_q = count_q.where(Recipe.source_type == source_type)

    total = (await db.execute(count_q)).scalar_one()
    offset = (page - 1) * per_page
    items = (await db.execute(query.offset(offset).limit(per_page))).scalars().unique().all()

    return list(items), total


async def get_recipe_by_id(db: AsyncSession, recipe_id: int, user_id: str) -> Recipe | None:
    result = await db.execute(
        _recipe_query()
        .where(Recipe.id == recipe_id, Recipe.user_id == uuid.UUID(user_id))
    )
    return result.scalar_one_or_none()


async def create_recipe(db: AsyncSession, data: RecipeCreate, user_id: str) -> Recipe:
    recipe = Recipe(
        user_id=uuid.UUID(user_id),
        title=data.title,
        description=data.description,
        servings=data.servings,
        prep_time=data.prep_time,
        cook_time=data.cook_time,
        total_time=data.total_time,
        image_url=data.image_url,
        source_url=data.source_url,
        source_type=data.source_type,
        notes=data.notes,
    )
    db.add(recipe)
    await db.flush()

    # 조리 단계
    for step_in in data.steps:
        db.add(RecipeStep(
            recipe_id=recipe.id,
            step_number=step_in.step_number,
            instruction=step_in.instruction,
            image_url=step_in.image_url,
        ))

    # 재료
    for i, ing_in in enumerate(data.ingredients):
        ingredient = await _get_or_create_ingredient(db, ing_in.name)
        db.add(RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            amount=ing_in.amount,
            unit=ing_in.unit,
            note=ing_in.note,
            sort_order=ing_in.sort_order or i,
        ))

    # 태그
    for tag_id in data.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id == tag_id))
        if result.scalar_one_or_none():
            db.add(RecipeTag(recipe_id=recipe.id, tag_id=tag_id))

    await db.flush()
    await db.refresh(recipe)
    return await get_recipe_by_id(db, recipe.id, user_id)


async def update_recipe(db: AsyncSession, recipe_id: int, data: RecipeUpdate, user_id: str) -> Recipe | None:
    recipe = await get_recipe_by_id(db, recipe_id, user_id)
    if not recipe:
        return None

    for field, value in data.model_dump(exclude_none=True, exclude={"steps", "ingredients", "tag_ids"}).items():
        setattr(recipe, field, value)

    if data.steps is not None:
        for step in recipe.steps:
            await db.delete(step)
        await db.flush()
        for step_in in data.steps:
            db.add(RecipeStep(
                recipe_id=recipe.id,
                step_number=step_in.step_number,
                instruction=step_in.instruction,
                image_url=step_in.image_url,
            ))

    if data.ingredients is not None:
        for ri in recipe.recipe_ingredients:
            await db.delete(ri)
        await db.flush()
        for i, ing_in in enumerate(data.ingredients):
            ingredient = await _get_or_create_ingredient(db, ing_in.name)
            db.add(RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                amount=ing_in.amount,
                unit=ing_in.unit,
                note=ing_in.note,
                sort_order=ing_in.sort_order or i,
            ))

    if data.tag_ids is not None:
        for rt in recipe.recipe_tags:
            await db.delete(rt)
        await db.flush()
        for tag_id in data.tag_ids:
            db.add(RecipeTag(recipe_id=recipe.id, tag_id=tag_id))

    await db.flush()
    return await get_recipe_by_id(db, recipe.id, user_id)


async def delete_recipe(db: AsyncSession, recipe_id: int, user_id: str) -> bool:
    recipe = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.user_id == uuid.UUID(user_id))
    )
    recipe = recipe.scalar_one_or_none()
    if not recipe:
        return False
    await db.delete(recipe)
    return True
