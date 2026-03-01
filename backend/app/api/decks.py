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
from app.schemas.deck import (
    DeckCreateRequest,
    DeckListResponse,
    DeckResponse,
    DeckStatsResponse,
    DeckUpdateRequest,
)

router = APIRouter(prefix="/decks", tags=["decks"])


def _get_owned_deck_or_404(db: Session, deck_id: int, user_id: int) -> Deck:
    deck = db.scalar(select(Deck).where(Deck.id == deck_id, Deck.user_id == user_id))
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return deck


def _now_utc() -> datetime:
    return datetime.now(UTC)


@router.post("", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
def create_deck(
    payload: DeckCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Deck:
    deck = Deck(user_id=current_user.id, name=payload.name)
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


@router.get("", response_model=DeckListResponse)
def list_decks(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeckListResponse:
    offset = (page - 1) * size
    total = db.scalar(select(func.count(Deck.id)).where(Deck.user_id == current_user.id)) or 0
    items = db.scalars(
        select(Deck)
        .where(Deck.user_id == current_user.id)
        .order_by(Deck.id.desc())
        .offset(offset)
        .limit(size)
    ).all()
    return DeckListResponse(items=items, page=page, size=size, total=total)


@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Deck:
    return _get_owned_deck_or_404(db, deck_id, current_user.id)


@router.get("/{deck_id}/stats", response_model=DeckStatsResponse)
def get_deck_stats(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeckStatsResponse:
    _get_owned_deck_or_404(db, deck_id, current_user.id)

    total_words = db.scalar(
        select(func.count(Word.id)).where(Word.deck_id == deck_id, Word.user_id == current_user.id)
    ) or 0

    total_reviews = db.scalar(
        select(func.count(ReviewLog.id))
        .join(Word, Word.id == ReviewLog.word_id)
        .where(
            ReviewLog.user_id == current_user.id,
            Word.deck_id == deck_id,
            Word.user_id == current_user.id,
        )
    ) or 0

    now = _now_utc()
    # Use server UTC date boundaries for MVP consistency.
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_day_start = day_start + timedelta(days=1)
    reviews_today = db.scalar(
        select(func.count(ReviewLog.id))
        .join(Word, Word.id == ReviewLog.word_id)
        .where(
            ReviewLog.user_id == current_user.id,
            Word.deck_id == deck_id,
            Word.user_id == current_user.id,
            ReviewLog.reviewed_at >= day_start,
            ReviewLog.reviewed_at < next_day_start,
        )
    ) or 0

    due_words_count = db.scalar(
        select(func.count(Word.id)).where(
            Word.deck_id == deck_id,
            Word.user_id == current_user.id,
            Word.due_at.is_not(None),
            Word.due_at <= now,
        )
    ) or 0
    new_words_count = db.scalar(
        select(func.count(Word.id)).where(
            Word.deck_id == deck_id,
            Word.user_id == current_user.id,
            Word.repetition == 0,
            Word.due_at.is_(None),
        )
    ) or 0
    queue_limit = 20
    remaining = max(0, queue_limit - due_words_count)
    due_count = min(queue_limit, due_words_count + min(remaining, new_words_count))

    return DeckStatsResponse(
        total_words=total_words,
        total_reviews=total_reviews,
        reviews_today=reviews_today,
        due_count=due_count,
    )


@router.put("/{deck_id}", response_model=DeckResponse)
def update_deck(
    deck_id: int,
    payload: DeckUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Deck:
    deck = _get_owned_deck_or_404(db, deck_id, current_user.id)
    deck.name = payload.name
    db.commit()
    db.refresh(deck)
    return deck


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    deck = _get_owned_deck_or_404(db, deck_id, current_user.id)
    db.delete(deck)
    db.commit()
    return None
