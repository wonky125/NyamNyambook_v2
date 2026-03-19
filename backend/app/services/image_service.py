"""이미지 업로드 — Supabase Storage"""
import uuid

from fastapi import UploadFile

from app.config import settings


async def upload_recipe_image(file: UploadFile, user_id: str) -> str:
    """
    Supabase Storage에 이미지를 업로드하고 공개 URL을 반환한다.
    supabase-py를 사용하면 동기 코드이지만 FastAPI에서 run_in_executor로 처리.
    """
    from supabase import create_client
    import asyncio

    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    ext = (file.filename or "image.jpg").rsplit(".", 1)[-1].lower()
    path = f"recipes/{user_id}/{uuid.uuid4()}.{ext}"
    content = await file.read()

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: client.storage.from_("recipe-images").upload(path, content, {"content-type": file.content_type}),
    )

    public_url = client.storage.from_("recipe-images").get_public_url(path)
    return public_url
