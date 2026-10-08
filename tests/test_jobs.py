import pytest
from unittest.mock import patch
from tests.conftest import VALID_PAYLOAD


def test_create_job_returns_202(client):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    assert resp.status_code == 202


def test_create_job_response_fields(client):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    data = resp.json()
    assert "id" in data
    assert data["event_name"] == VALID_PAYLOAD["event_name"]
    assert data["issued_by"] == VALID_PAYLOAD["issued_by"]
    assert data["total"] == len(VALID_PAYLOAD["recipients"])
    assert data["status"] == "pending"


def test_create_job_dispatches_celery_task(client):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    assert resp.status_code == 202


def test_create_job_persists_certificates(client, db):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    job_id = resp.json()["id"]

    from app.models import Certificate
    certs = db.query(Certificate).filter(Certificate.job_id == job_id).all()
    assert len(certs) == 2


def test_list_jobs(client):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        client.post("/api/v1/jobs", json=VALID_PAYLOAD)
        client.post("/api/v1/jobs", json=VALID_PAYLOAD)

    resp = client.get("/api/v1/jobs")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_get_job_not_found(client):
    resp = client.get("/api/v1/jobs/nonexistent-id")
    assert resp.status_code == 404
