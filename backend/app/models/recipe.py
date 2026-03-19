import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, Text, Uuid, func, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    title: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    servings: Mapped[str | None] = mapped_column(VARCHAR(50), nullable=True)
    prep_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cook_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cooked_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    steps: Mapped[list["RecipeStep"]] = relationship(
        "RecipeStep", back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeStep.step_number"
    )
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeIngredient.sort_order"
    )
    recipe_tags: Mapped[list["RecipeTag"]] = relationship(
        "RecipeTag", back_populates="recipe", cascade="all, delete-orphan"
    )
    cook_logs: Mapped[list["CookLog"]] = relationship(
        "CookLog", back_populates="recipe", cascade="all, delete-orphan"
    )
