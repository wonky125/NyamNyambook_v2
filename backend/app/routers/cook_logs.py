"""요리 이력 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.cook_log import CookLogResponse
from app.services.cook_log_service import get_cook_logs, log_cooked

router = APIRouter()


@router.post("/{recipe_id}/cook", response_model=CookLogResponse, status_code=status.HTTP_201_CREATED)
async def mark_cooked(
    recipe_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = await log_cooked(db, recipe_id, user_id)
    if not log:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
    return log


@router.get("/{recipe_id}/cook", response_model=list[CookLogResponse])
async def get_logs(
    recipe_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_cook_logs(db, recipe_id, user_id)
