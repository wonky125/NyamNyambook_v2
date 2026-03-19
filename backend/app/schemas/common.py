from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
