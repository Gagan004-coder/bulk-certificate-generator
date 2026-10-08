import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_certs.db"

from app.main import app
from app.database import Base, get_db
from app.models import Job, Certificate, JobStatus, CertificateStatus

TEST_DATABASE_URL = "sqlite:///./test_certs.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


VALID_PAYLOAD = {
    "event_name": "Python Bootcamp 2024",
    "issued_by": "Tech Academy",
    "recipients": [
        {"name": "Alice Smith", "email": "alice@example.com", "completion_date": "2024-05-01"},
        {"name": "Bob Jones", "email": "bob@example.com", "completion_date": "2024-05-01"},
    ],
}
