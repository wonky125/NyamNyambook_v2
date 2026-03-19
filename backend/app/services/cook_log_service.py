"""요리 이력(cook_log) 서비스"""
import uuid

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cook_log import CookLog
from app.models.recipe import Recipe


async def log_cooked(db: AsyncSession, recipe_id: int, user_id: str) -> CookLog | None:
    # 레시피 소유 확인
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.user_id == uuid.UUID(user_id))
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        return None

    log = CookLog(recipe_id=recipe_id, user_id=uuid.UUID(user_id))
    db.add(log)
    recipe.cooked_count += 1
    await db.flush()
    await db.refresh(log)
    return log


async def get_cook_logs(db: AsyncSession, recipe_id: int, user_id: str) -> list[CookLog]:
    result = await db.execute(
        select(CookLog)
        .where(CookLog.recipe_id == recipe_id, CookLog.user_id == uuid.UUID(user_id))
        .order_by(desc(CookLog.cooked_at))
    )
    return list(result.scalars().all())
