"""이미지 업로드 라우터"""
from fastapi import APIRouter, Depends, File, UploadFile

from app.dependencies import get_current_user
from app.services.image_service import upload_recipe_image

router = APIRouter()


@router.post("")
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    url = await upload_recipe_image(file, user_id)
    return {"url": url}
