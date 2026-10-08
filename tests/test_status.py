import os
import tempfile
import pytest
from unittest.mock import patch
from tests.conftest import VALID_PAYLOAD


def test_job_status_pending_after_creation(client):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    job_id = resp.json()["id"]

    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["status"] in ("pending", "processing", "completed")
    assert data["total"] == 2


def test_job_status_includes_certificates(client):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    job_id = resp.json()["id"]

    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    data = status_resp.json()
    assert "certificates" in data
    assert len(data["certificates"]) == 2


def test_job_status_certificate_fields(client):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    job_id = resp.json()["id"]

    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    cert = status_resp.json()["certificates"][0]
    assert "id" in cert
    assert "recipient_name" in cert
    assert "recipient_email" in cert
    assert "status" in cert
    assert "completion_date" in cert


def test_get_certificates_for_job(client):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    job_id = resp.json()["id"]

    certs_resp = client.get(f"/api/v1/jobs/{job_id}/certificates")
    assert certs_resp.status_code == 200
    assert len(certs_resp.json()) == 2


def test_job_counters_after_processing(client, db):
    with patch("app.routes.process_job") as mock_task:
        mock_task.delay = lambda job_id: None
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)
    job_id = resp.json()["id"]

    from app.models import Job, Certificate, JobStatus, CertificateStatus
    from tests.conftest import TestingSessionLocal

    s = TestingSessionLocal()
    job = s.query(Job).filter(Job.id == job_id).first()
    certs = s.query(Certificate).filter(Certificate.job_id == job_id).all()
    for c in certs:
        c.status = CertificateStatus.success
        c.file_path = "/fake/path.pdf"
    job.status = JobStatus.completed
    job.succeeded = 2
    job.failed = 0
    s.commit()
    s.close()

    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    data = status_resp.json()
    assert data["succeeded"] == 2
    assert data["failed"] == 0
    assert data["status"] == "completed"
