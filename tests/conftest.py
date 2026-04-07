import os

os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db
from app.db.models import Base

# Create SQLite in-memory database configuration for extreme speed in CI
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for sqlite and FastAPI
    poolclass=StaticPool,  # keeps the in-memory db intact across sessions
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database():
    # Set up tables once per suite
    Base.metadata.create_all(bind=engine)
    yield
    # Tear down tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(setup_database):
    # Ensure fresh session per test
    session = TestingSessionLocal()
    try:
        # clear any data from previous tests
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    # Dependency override for testing
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session closed by db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    # Clean up override so it doesn't leak
    app.dependency_overrides.clear()
