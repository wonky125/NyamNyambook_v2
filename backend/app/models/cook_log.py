import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CookLog(Base):
    __tablename__ = "cook_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    cooked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)   # Phase 3
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)             # Phase 3

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="cook_logs")
