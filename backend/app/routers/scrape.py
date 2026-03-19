"""스크래핑 API"""
from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.scrape import ScrapeRequest, ScrapeResult
from app.services.scrape_service import scrape_url

router = APIRouter()


@router.post("", response_model=ScrapeResult)
async def scrape_recipe_url(
    body: ScrapeRequest,
    _user_id: str = Depends(get_current_user),
):
    """
    URL을 스크래핑해서 레시피 데이터를 반환한다.
    실패해도 400 에러가 아닌 scrape_success=False 결과를 반환한다.
    """
    return await scrape_url(body.url)
