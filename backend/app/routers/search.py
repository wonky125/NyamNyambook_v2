"""검색 라우터"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.recipe import RecipeSummary
from app.services.search_service import search_recipes

router = APIRouter()


@router.get("", response_model=list[RecipeSummary])
async def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await search_recipes(db, user_id, q, page, per_page)
