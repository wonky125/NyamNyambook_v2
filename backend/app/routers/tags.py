"""태그 라우터"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.tag import TagCreate, TagResponse
from app.services.tag_service import create_tag, get_all_tags

router = APIRouter()


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    return await get_all_tags(db)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def add_tag(
    body: TagCreate,
    _user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_tag(db, body)
