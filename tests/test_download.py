import pytest
from unittest.mock import patch
from tests.conftest import VALID_PAYLOAD, TestingSessionLocal
from app.models import Job, Certificate, JobStatus, CertificateStatus

FAKE_PDF = b"%PDF-1.4 fake content"


def test_download_certificate_not_ready(client):
    with patch("app.routes.process_job"):
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)

    job_id = resp.json()["id"]
    s = TestingSessionLocal()
    cert = s.query(Certificate).filter(Certificate.job_id == job_id).first()
    cert_id = cert.id
    s.close()

    dl = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert dl.status_code == 409


def test_download_certificate_not_found(client):
    dl = client.get("/api/v1/certificates/nonexistent/download")
    assert dl.status_code == 404


def test_download_certificate_success(client):
    with patch("app.routes.process_job"):
        resp = client.post("/api/v1/jobs", json=VALID_PAYLOAD)

    job_id = resp.json()["id"]

    s = TestingSessionLocal()
    cert = s.query(Certificate).filter(Certificate.job_id == job_id).first()
    cert.status = CertificateStatus.success
    cert.file_data = FAKE_PDF
    s.commit()
    cert_id = cert.id
    s.close()

    dl = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert dl.status_code == 200
    assert dl.headers["content-type"] == "application/pdf"
    assert dl.content == FAKE_PDF
