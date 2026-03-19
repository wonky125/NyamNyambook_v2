"""태그 CRUD + 사용자 태그 조회"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag, RecipeTag
from app.schemas.tag import TagCreate


async def get_all_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.category, Tag.name))
    return list(result.scalars().all())


async def get_or_create_tag(db: AsyncSession, name: str, category: str | None = None) -> Tag:
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name, category=category)
        db.add(tag)
        await db.flush()
    return tag


async def create_tag(db: AsyncSession, data: TagCreate) -> Tag:
    return await get_or_create_tag(db, data.name, data.category)
