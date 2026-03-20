"""장보기 리스트 라우터"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.shopping_item import ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse
from app.services import shopping_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("", response_model=list[ShoppingItemResponse])
async def list_items(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await shopping_service.get_items(db, user_id)


@router.post("", response_model=ShoppingItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    body: ShoppingItemCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await shopping_service.create_item(db, body, user_id)


@router.patch("/{item_id}", response_model=ShoppingItemResponse)
async def update_item(
    item_id: int,
    body: ShoppingItemUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await shopping_service.toggle_item(db, item_id, body.is_checked, user_id)
    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await shopping_service.delete_item(db, item_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_checked_items(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """체크된 항목 일괄 삭제"""
    await shopping_service.clear_checked(db, user_id)
