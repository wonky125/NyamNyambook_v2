from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShoppingItemCreate(BaseModel):
    name: str


class ShoppingItemUpdate(BaseModel):
    is_checked: bool


class ShoppingItemResponse(BaseModel):
    id: int
    name: str
    is_checked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
