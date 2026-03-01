from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReviewLog(Base):
    __tablename__ = "review_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"), index=True, nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    prev_repetition: Mapped[int] = mapped_column(Integer, nullable=False)
    prev_interval: Mapped[int] = mapped_column(Integer, nullable=False)
    prev_ease_factor: Mapped[float] = mapped_column(Float, nullable=False)
    prev_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    next_repetition: Mapped[int] = mapped_column(Integer, nullable=False)
    next_interval: Mapped[int] = mapped_column(Integer, nullable=False)
    next_ease_factor: Mapped[float] = mapped_column(Float, nullable=False)
    next_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

