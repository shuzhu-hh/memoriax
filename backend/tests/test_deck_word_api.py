from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


def _build_test_client() -> TestClient:
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
    return TestClient(app)


def _register_and_login(client: TestClient, email: str) -> str:
    password = "StrongPass123"
    register_payload = {"email": email, "password": password}
    register_resp = client.post("/auth/register", json=register_payload)
    assert register_resp.status_code == 201
    login_resp = client.post("/auth/login", json=register_payload)
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


def test_deck_word_crud_and_import() -> None:
    client = _build_test_client()
    try:
        token = _register_and_login(client, "owner@example.com")
        headers = {"Authorization": f"Bearer {token}"}

        create_deck_resp = client.post("/decks", json={"name": "My Deck"}, headers=headers)
        assert create_deck_resp.status_code == 201
        deck_id = create_deck_resp.json()["id"]

        list_decks_resp = client.get("/decks?page=1&size=10", headers=headers)
        assert list_decks_resp.status_code == 200
        assert list_decks_resp.json()["total"] == 1

        update_deck_resp = client.put(f"/decks/{deck_id}", json={"name": "Deck Renamed"}, headers=headers)
        assert update_deck_resp.status_code == 200
        assert update_deck_resp.json()["name"] == "Deck Renamed"

        create_word_resp = client.post(
            f"/decks/{deck_id}/words",
            json={"word": "hello", "definition": "你好"},
            headers=headers,
        )
        assert create_word_resp.status_code == 201
        word_id = create_word_resp.json()["id"]

        list_words_resp = client.get(f"/decks/{deck_id}/words?page=1&size=10", headers=headers)
        assert list_words_resp.status_code == 200
        assert list_words_resp.json()["total"] == 1

        import_resp = client.post(
            f"/decks/{deck_id}/words/import",
            json={"content": "apple\t苹果\nbanana"},
            headers=headers,
        )
        assert import_resp.status_code == 201
        assert import_resp.json()["imported_count"] == 2

        get_word_resp = client.get(f"/words/{word_id}", headers=headers)
        assert get_word_resp.status_code == 200

        update_word_resp = client.put(
            f"/words/{word_id}",
            json={"word": "hello2", "definition": "问候"},
            headers=headers,
        )
        assert update_word_resp.status_code == 200
        assert update_word_resp.json()["word"] == "hello2"

        delete_word_resp = client.delete(f"/words/{word_id}", headers=headers)
        assert delete_word_resp.status_code == 204

        delete_deck_resp = client.delete(f"/decks/{deck_id}", headers=headers)
        assert delete_deck_resp.status_code == 204
    finally:
        app.dependency_overrides.clear()


def test_cross_user_access_returns_404() -> None:
    client = _build_test_client()
    try:
        token_user_a = _register_and_login(client, "a@example.com")
        token_user_b = _register_and_login(client, "b@example.com")
        headers_a = {"Authorization": f"Bearer {token_user_a}"}
        headers_b = {"Authorization": f"Bearer {token_user_b}"}

        create_deck_resp = client.post("/decks", json={"name": "A Deck"}, headers=headers_a)
        assert create_deck_resp.status_code == 201
        deck_id = create_deck_resp.json()["id"]

        create_word_resp = client.post(
            f"/decks/{deck_id}/words",
            json={"word": "secret", "definition": "only A"},
            headers=headers_a,
        )
        assert create_word_resp.status_code == 201
        word_id = create_word_resp.json()["id"]

        # User B should never see User A resources.
        assert client.get(f"/decks/{deck_id}", headers=headers_b).status_code == 404
        assert client.put(f"/decks/{deck_id}", json={"name": "hack"}, headers=headers_b).status_code == 404
        assert client.delete(f"/decks/{deck_id}", headers=headers_b).status_code == 404
        assert client.get(f"/decks/{deck_id}/words", headers=headers_b).status_code == 404

        assert client.get(f"/words/{word_id}", headers=headers_b).status_code == 404
        assert (
            client.put(f"/words/{word_id}", json={"word": "x", "definition": "y"}, headers=headers_b).status_code
            == 404
        )
        assert client.delete(f"/words/{word_id}", headers=headers_b).status_code == 404
    finally:
        app.dependency_overrides.clear()

