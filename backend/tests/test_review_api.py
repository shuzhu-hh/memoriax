from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.review_log import ReviewLog
from app.models.word import Word


def _build_test_client() -> tuple[TestClient, sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), testing_session_local


def _register_and_login(client: TestClient, email: str) -> str:
    password = "StrongPass123"
    payload = {"email": email, "password": password}
    assert client.post("/auth/register", json=payload).status_code == 201
    login_resp = client.post("/auth/login", json=payload)
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


def test_review_queue_review_and_stats() -> None:
    client, session_factory = _build_test_client()
    try:
        token = _register_and_login(client, "reviewer@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        deck_resp = client.post("/decks", json={"name": "Review Deck"}, headers=headers)
        assert deck_resp.status_code == 201
        deck_id = deck_resp.json()["id"]

        import_resp = client.post(
            f"/decks/{deck_id}/words/import",
            json={"content": "alpha\tfirst\nbeta"},
            headers=headers,
        )
        assert import_resp.status_code == 201
        assert import_resp.json()["imported_count"] == 2

        queue_resp = client.get(f"/reviews/queue?deck_id={deck_id}&limit=20", headers=headers)
        assert queue_resp.status_code == 200
        queue_items = queue_resp.json()
        assert len(queue_items) == 2
        assert queue_items[0]["is_new"] is True

        word_id = queue_items[0]["word_id"]
        review_resp = client.post(f"/reviews/{word_id}", json={"grade": 4}, headers=headers)
        assert review_resp.status_code == 200
        reviewed = review_resp.json()
        assert reviewed["repetition"] == 1
        assert reviewed["interval"] == 1
        assert reviewed["due_at"] is not None

        with session_factory() as db:
            log_count = db.scalar(select(func.count(ReviewLog.id)).where(ReviewLog.word_id == word_id))
            assert log_count == 1
            word = db.get(Word, word_id)
            assert word is not None
            assert word.repetition == 1

        stats_resp = client.get(f"/reviews/stats?deck_id={deck_id}", headers=headers)
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert "today_due_count" in stats
        assert "total_due_count" in stats
        assert "learned_count" in stats
        assert "new_count" in stats
        assert len(stats["next_7_days_due"]) == 7
    finally:
        app.dependency_overrides.clear()


def test_review_forbidden_cross_user_returns_404() -> None:
    client, _ = _build_test_client()
    try:
        token_a = _register_and_login(client, "a.review@example.com")
        token_b = _register_and_login(client, "b.review@example.com")
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        deck_resp = client.post("/decks", json={"name": "A Deck"}, headers=headers_a)
        deck_id = deck_resp.json()["id"]
        word_resp = client.post(
            f"/decks/{deck_id}/words",
            json={"word": "private", "definition": "a"},
            headers=headers_a,
        )
        word_id = word_resp.json()["id"]

        assert client.post(f"/reviews/{word_id}", json={"grade": 3}, headers=headers_b).status_code == 404
        assert client.get("/reviews/queue", headers=headers_b).status_code == 200
        assert client.get(f"/reviews/queue?deck_id={deck_id}", headers=headers_b).status_code == 404
        assert client.get(f"/reviews/stats?deck_id={deck_id}", headers=headers_b).status_code == 404
    finally:
        app.dependency_overrides.clear()
