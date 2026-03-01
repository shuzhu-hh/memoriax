from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.deck import Deck


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    word: Mapped[str] = mapped_column(String(255), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=True)
    ease_factor: Mapped[float] = mapped_column(Float, nullable=False, default=2.5, server_default="2.5")
    interval: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    repetition: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    deck: Mapped["Deck"] = relationship("Deck", back_populates="words")
