import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_user
from app.models.deck import Deck
from app.models.user import User
from app.models.word import Word
from app.schemas.word import (
    WordCreateRequest,
    WordImportRequest,
    WordImportResponse,
    WordListResponse,
    WordResponse,
    WordUpdateRequest,
)

router = APIRouter(tags=["words"])


def _get_owned_deck_or_404(db: Session, deck_id: int, user_id: int) -> Deck:
    deck = db.scalar(select(Deck).where(Deck.id == deck_id, Deck.user_id == user_id))
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return deck


def _get_owned_word_or_404(db: Session, word_id: int, user_id: int) -> Word:
    word = db.scalar(select(Word).where(Word.id == word_id, Word.user_id == user_id))
    if word is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")
    return word


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value.strip())


def _word_key(word: str, definition: str | None) -> str:
    return f"{_normalize_text(word)}||{_normalize_text(definition)}"


@router.post("/decks/{deck_id}/words", response_model=WordResponse, status_code=status.HTTP_201_CREATED)
def create_word(
    deck_id: int,
    payload: WordCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Word:
    _get_owned_deck_or_404(db, deck_id, current_user.id)
    incoming_key = _word_key(payload.word, payload.definition)
    existing_rows = db.execute(
        select(Word.word, Word.definition).where(Word.deck_id == deck_id, Word.user_id == current_user.id)
    ).all()
    existing_keys = {_word_key(word_text, definition) for word_text, definition in existing_rows}
    if incoming_key in existing_keys:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该单词已存在，无需重复添加")

    word = Word(
        deck_id=deck_id,
        user_id=current_user.id,
        word=payload.word,
        definition=payload.definition,
    )
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


@router.get("/decks/{deck_id}/words", response_model=WordListResponse)
def list_words(
    deck_id: int,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WordListResponse:
    _get_owned_deck_or_404(db, deck_id, current_user.id)
    offset = (page - 1) * size
    total = db.scalar(
        select(func.count(Word.id)).where(Word.deck_id == deck_id, Word.user_id == current_user.id)
    ) or 0
    items = db.scalars(
        select(Word)
        .where(Word.deck_id == deck_id, Word.user_id == current_user.id)
        .order_by(Word.id.desc())
        .offset(offset)
        .limit(size)
    ).all()
    return WordListResponse(items=items, page=page, size=size, total=total)


@router.get("/words/{word_id}", response_model=WordResponse)
def get_word(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Word:
    return _get_owned_word_or_404(db, word_id, current_user.id)


@router.put("/words/{word_id}", response_model=WordResponse)
def update_word(
    word_id: int,
    payload: WordUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Word:
    word = _get_owned_word_or_404(db, word_id, current_user.id)
    word.word = payload.word
    word.definition = payload.definition
    db.commit()
    db.refresh(word)
    return word


@router.delete("/words/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    word = _get_owned_word_or_404(db, word_id, current_user.id)
    db.delete(word)
    db.commit()
    return None


@router.post("/decks/{deck_id}/words/import", response_model=WordImportResponse, status_code=status.HTTP_201_CREATED)
def import_words(
    deck_id: int,
    payload: WordImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WordImportResponse:
    _get_owned_deck_or_404(db, deck_id, current_user.id)

    existing_rows = db.execute(
        select(Word.word, Word.definition).where(Word.deck_id == deck_id, Word.user_id == current_user.id)
    ).all()
    existing_keys = {_word_key(word_text, definition) for word_text, definition in existing_rows}

    to_create: list[Word] = []
    seen_in_payload: set[str] = set()
    skipped_count = 0
    for raw_line in payload.content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = re.split(r"\s+", line, maxsplit=1)
        word_text = parts[0].strip()
        definition = parts[1].strip() if len(parts) > 1 else None
        if definition == "":
            definition = None
        if not word_text:
            continue
        key = _word_key(word_text, definition)
        if key in seen_in_payload:
            continue
        seen_in_payload.add(key)
        if key in existing_keys:
            skipped_count += 1
            continue
        to_create.append(
            Word(
                deck_id=deck_id,
                user_id=current_user.id,
                word=word_text,
                definition=definition,
            )
        )

    if to_create:
        db.add_all(to_create)
        db.commit()

    return WordImportResponse(imported_count=len(to_create), skipped_count=skipped_count)
