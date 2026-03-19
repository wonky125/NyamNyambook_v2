import uuid
from datetime import datetime

from pydantic import BaseModel


class CookLogCreate(BaseModel):
    recipe_id: int


class CookLogResponse(BaseModel):
    id: int
    recipe_id: int
    user_id: uuid.UUID
    cooked_at: datetime

    model_config = {"from_attributes": True}
