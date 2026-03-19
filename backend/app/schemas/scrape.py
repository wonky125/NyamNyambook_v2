from pydantic import BaseModel


class ScrapeRequest(BaseModel):
    url: str


class ScrapedIngredient(BaseModel):
    name: str
    amount: str | None = None
    unit: str | None = None
    note: str | None = None


class ScrapedStep(BaseModel):
    step_number: int
    instruction: str
    image_url: str | None = None


class ScrapeResult(BaseModel):
    """스크래핑 결과 — RecipeCreate로 변환 후 저장"""
    title: str | None = None
    description: str | None = None
    servings: str | None = None
    prep_time: int | None = None
    cook_time: int | None = None
    total_time: int | None = None
    image_url: str | None = None
    source_url: str
    source_type: str = "web"
    steps: list[ScrapedStep] = []
    ingredients: list[ScrapedIngredient] = []
    suggested_tags: list[str] = []
    scrape_success: bool = True
