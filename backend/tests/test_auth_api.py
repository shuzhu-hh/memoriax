from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


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


def test_register_login_and_me() -> None:
    client, _ = _build_test_client()
    try:
        register_payload = {"email": "user@example.com", "password": "StrongPass123"}
        register_resp = client.post("/auth/register", json=register_payload)
        assert register_resp.status_code == 201
        assert register_resp.json()["email"] == "user@example.com"

        bad_login_resp = client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "WrongPassword"},
        )
        assert bad_login_resp.status_code == 401

        login_resp = client.post("/auth/login", json=register_payload)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        assert token

        me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "user@example.com"
    finally:
        app.dependency_overrides.clear()


def test_register_rejects_password_over_72_utf8_bytes() -> None:
    client, _ = _build_test_client()
    try:
        payload = {"email": "long@example.com", "password": "a" * 73}
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 422
        assert "72 bytes" in resp.json()["detail"]
    finally:
        app.dependency_overrides.clear()
