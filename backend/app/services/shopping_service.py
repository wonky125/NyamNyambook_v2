"""장보기 리스트 비즈니스 로직"""
import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping_item import ShoppingItem
from app.schemas.shopping_item import ShoppingItemCreate


async def get_items(db: AsyncSession, user_id: str) -> list[ShoppingItem]:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(ShoppingItem)
        .where(ShoppingItem.user_id == uid)
        .order_by(ShoppingItem.created_at.asc())
    )
    return list(result.scalars().all())


async def create_item(db: AsyncSession, body: ShoppingItemCreate, user_id: str) -> ShoppingItem:
    item = ShoppingItem(user_id=uuid.UUID(user_id), name=body.name.strip())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def toggle_item(db: AsyncSession, item_id: int, is_checked: bool, user_id: str) -> ShoppingItem | None:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(ShoppingItem).where(ShoppingItem.id == item_id, ShoppingItem.user_id == uid)
    )
    item = result.scalar_one_or_none()
    if not item:
        return None
    item.is_checked = is_checked
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item_id: int, user_id: str) -> bool:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        delete(ShoppingItem).where(ShoppingItem.id == item_id, ShoppingItem.user_id == uid)
    )
    await db.commit()
    return result.rowcount > 0


async def clear_checked(db: AsyncSession, user_id: str) -> int:
    """체크된 항목 일괄 삭제. 삭제된 행 수 반환."""
    uid = uuid.UUID(user_id)
    result = await db.execute(
        delete(ShoppingItem).where(ShoppingItem.user_id == uid, ShoppingItem.is_checked == True)
    )
    await db.commit()
    return result.rowcount
