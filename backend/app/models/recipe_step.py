from sqlalchemy import ForeignKey, Integer, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    step_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="steps")
