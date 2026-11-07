import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def create_person(client):
    return client.post(
        "/api/v1/persons",
        json={
            "name": "Ivan",
            "age": 25,
            "address": "Moscow",
            "work": "Developer",
        },
    )


def test_get_persons_empty(client):
    response = client.get("/api/v1/persons")

    assert response.status_code == 200
    assert response.json() == []


def test_create_person(client):
    response = create_person(client)

    assert response.status_code == 201
    assert response.text == ""
    assert response.headers["location"] == "/api/v1/persons/1"


def test_get_person(client):
    create_person(client)

    response = client.get("/api/v1/persons/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Ivan"
    assert response.json()["age"] == 25


def test_update_person(client):
    create_person(client)

    response = client.patch(
        "/api/v1/persons/1",
        json={"age": 26},
    )

    assert response.status_code == 200
    assert response.json()["age"] == 26
    assert response.json()["name"] == "Ivan"


def test_delete_person(client):
    create_person(client)

    response = client.delete("/api/v1/persons/1")

    assert response.status_code == 204
    assert response.text == ""

    response = client.get("/api/v1/persons/1")

    assert response.status_code == 404
