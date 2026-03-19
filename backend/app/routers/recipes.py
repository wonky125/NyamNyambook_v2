"""레시피 CRUD 라우터"""
import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.common import PaginationMeta
from app.schemas.recipe import RecipeCreate, RecipeDetail, RecipeSummary, RecipeUpdate
from app.services import recipe_service

router = APIRouter()


@router.get("", response_model=dict)
async def list_recipes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    tag_id: int | None = None,
    source_type: str | None = None,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipes, total = await recipe_service.get_user_recipes(
        db, user_id, page, per_page, tag_id, source_type
    )
    return {
        "items": [RecipeSummary.model_validate(r) for r in recipes],
        "meta": PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=math.ceil(total / per_page) if total else 0,
        ),
    }


@router.post("", response_model=RecipeDetail, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    body: RecipeCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await recipe_service.create_recipe(db, body, user_id)


@router.get("/{recipe_id}", response_model=RecipeDetail)
async def get_recipe(
    recipe_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipe = await recipe_service.get_recipe_by_id(db, recipe_id, user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
    return recipe


@router.put("/{recipe_id}", response_model=RecipeDetail)
async def update_recipe(
    recipe_id: int,
    body: RecipeUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipe = await recipe_service.update_recipe(db, recipe_id, body, user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await recipe_service.delete_recipe(db, recipe_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
