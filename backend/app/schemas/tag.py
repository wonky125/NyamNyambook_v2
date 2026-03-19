from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    category: str | None = None


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    model_config = {"from_attributes": True}
