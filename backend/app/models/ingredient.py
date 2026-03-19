from sqlalchemy import Integer, SmallInteger, ForeignKey, UniqueConstraint, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, unique=True, index=True)
    name_en: Mapped[str | None] = mapped_column(VARCHAR(100), nullable=True, index=True)

    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="ingredient"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[int] = mapped_column(Integer, ForeignKey("ingredients.id"), nullable=False)
    amount: Mapped[str | None] = mapped_column(VARCHAR(50), nullable=True)
    unit: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=True)
    note: Mapped[str | None] = mapped_column(VARCHAR(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="recipe_ingredients")
