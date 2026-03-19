from sqlalchemy import ForeignKey, Integer, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, unique=True, index=True)
    category: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=True)

    recipe_tags: Mapped[list["RecipeTag"]] = relationship("RecipeTag", back_populates="tag")


class RecipeTag(Base):
    __tablename__ = "recipe_tags"

    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="recipe_tags")
