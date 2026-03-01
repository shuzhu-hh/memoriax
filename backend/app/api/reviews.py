from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.models.deck import Deck
from app.models.review_log import ReviewLog
from app.models.user import User
from app.models.word import Word
from app.schemas.review import (
    DailyDueStat,
    ReviewGradeRequest,
    ReviewQueueItem,
    ReviewResultResponse,
    ReviewStatsResponse,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _ensure_owned_deck_or_404(db: Session, deck_id: int, user_id: int) -> None:
    deck_exists = db.scalar(select(Deck.id).where(Deck.id == deck_id, Deck.user_id == user_id))
    if deck_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")


def _get_owned_word_or_404(db: Session, word_id: int, user_id: int) -> Word:
    word = db.scalar(select(Word).where(Word.id == word_id, Word.user_id == user_id))
    if word is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    return word


@router.get("/queue", response_model=list[ReviewQueueItem])
def get_review_queue(
    deck_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReviewQueueItem]:
    if deck_id is not None:
        _ensure_owned_deck_or_404(db, deck_id, current_user.id)

    now = _now_utc()
    filters = [Word.user_id == current_user.id]
    if deck_id is not None:
        filters.append(Word.deck_id == deck_id)

    due_words = db.scalars(
        select(Word)
        .where(*filters, Word.due_at.is_not(None), Word.due_at <= now)
        .order_by(Word.due_at.asc(), Word.id.asc())
        .limit(limit)
    ).all()

    remaining = max(0, limit - len(due_words))
    new_words: list[Word] = []
    if remaining > 0:
        new_words = db.scalars(
            select(Word)
            .where(*filters, Word.repetition == 0, Word.due_at.is_(None))
            .order_by(Word.id.asc())
            .limit(remaining)
        ).all()

    items: list[ReviewQueueItem] = []
    for w in due_words:
        items.append(
            ReviewQueueItem(
                word_id=w.id,
                word=w.word,
                definition=w.definition,
                due_at=w.due_at,
                repetition=w.repetition,
                interval=w.interval,
                ease_factor=w.ease_factor,
                is_new=(w.repetition == 0 and w.due_at is None),
            )
        )
    for w in new_words:
        items.append(
            ReviewQueueItem(
                word_id=w.id,
                word=w.word,
                definition=w.definition,
                due_at=w.due_at,
                repetition=w.repetition,
                interval=w.interval,
                ease_factor=w.ease_factor,
                is_new=True,
            )
        )

    return items


@router.post("/{word_id}", response_model=ReviewResultResponse)
def review_word(
    word_id: int,
    payload: ReviewGradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewResultResponse:
    word = _get_owned_word_or_404(db, word_id, current_user.id)
    now = _now_utc()

    prev_repetition = word.repetition
    prev_interval = word.interval
    prev_ease_factor = word.ease_factor
    prev_due_at = word.due_at

    ease_factor = prev_ease_factor if prev_ease_factor > 0 else 2.5

    if payload.grade < 3:
        next_repetition = 0
        next_interval = 1
    else:
        next_repetition = prev_repetition + 1
        if next_repetition == 1:
            next_interval = 1
        elif next_repetition == 2:
            next_interval = 6
        else:
            base_interval = prev_interval if prev_interval > 0 else 1
            next_interval = max(1, round(base_interval * ease_factor))

    grade_distance = 5 - payload.grade
    ef_delta = 0.1 - grade_distance * (0.08 + grade_distance * 0.02)
    next_ease_factor = max(1.3, ease_factor + ef_delta)
    next_due_at = now + timedelta(days=next_interval)

    word.repetition = next_repetition
    word.interval = next_interval
    word.ease_factor = next_ease_factor
    word.due_at = next_due_at

    review_log = ReviewLog(
        user_id=current_user.id,
        word_id=word.id,
        grade=payload.grade,
        reviewed_at=now,
        prev_repetition=prev_repetition,
        prev_interval=prev_interval,
        prev_ease_factor=prev_ease_factor,
        prev_due_at=prev_due_at,
        next_repetition=next_repetition,
        next_interval=next_interval,
        next_ease_factor=next_ease_factor,
        next_due_at=next_due_at,
    )
    db.add(review_log)
    db.commit()
    db.refresh(word)

    return ReviewResultResponse(
        word_id=word.id,
        repetition=word.repetition,
        interval=word.interval,
        ease_factor=word.ease_factor,
        due_at=word.due_at,
    )


@router.get("/stats", response_model=ReviewStatsResponse)
def get_review_stats(
    deck_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewStatsResponse:
    if deck_id is not None:
        _ensure_owned_deck_or_404(db, deck_id, current_user.id)

    now = _now_utc()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_day_start = day_start + timedelta(days=1)

    filters = [Word.user_id == current_user.id]
    if deck_id is not None:
        filters.append(Word.deck_id == deck_id)

    today_due_count = db.scalar(
        select(func.count(Word.id)).where(
            *filters,
            Word.due_at.is_not(None),
            Word.due_at >= day_start,
            Word.due_at < next_day_start,
        )
    ) or 0

    total_due_count = db.scalar(
        select(func.count(Word.id)).where(*filters, Word.due_at.is_not(None), Word.due_at <= now)
    ) or 0

    learned_count = db.scalar(select(func.count(Word.id)).where(*filters, Word.repetition > 0)) or 0
    new_count = db.scalar(select(func.count(Word.id)).where(*filters, Word.repetition == 0)) or 0

    next_7_days_due: list[DailyDueStat] = []
    for day_offset in range(7):
        bucket_start = day_start + timedelta(days=day_offset)
        bucket_end = bucket_start + timedelta(days=1)
        due_count = db.scalar(
            select(func.count(Word.id)).where(
                *filters,
                Word.due_at.is_not(None),
                Word.due_at >= bucket_start,
                Word.due_at < bucket_end,
            )
        ) or 0
        next_7_days_due.append(DailyDueStat(date=bucket_start.date().isoformat(), due_count=due_count))

    return ReviewStatsResponse(
        today_due_count=today_due_count,
        total_due_count=total_due_count,
        learned_count=learned_count,
        new_count=new_count,
        next_7_days_due=next_7_days_due,
    )

