import os
import tempfile
import pytest
from app.certificate_generator import generate_certificate_pdf


@pytest.fixture(autouse=True)
def set_cert_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("app.certificate_generator.CERTIFICATES_DIR", str(tmp_path))


def test_generate_certificate_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("app.certificate_generator.CERTIFICATES_DIR", str(tmp_path))
    file_path = generate_certificate_pdf(
        job_id="job-1",
        cert_id="cert-1",
        recipient_name="Alice Smith",
        recipient_email="alice@example.com",
        event_name="Python Bootcamp",
        issued_by="Tech Academy",
        completion_date="2024-05-01",
    )
    assert os.path.exists(file_path)
    assert file_path.endswith(".pdf")


def test_generate_certificate_is_valid_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr("app.certificate_generator.CERTIFICATES_DIR", str(tmp_path))
    file_path = generate_certificate_pdf(
        job_id="job-2",
        cert_id="cert-2",
        recipient_name="Bob Jones",
        recipient_email="bob@example.com",
        event_name="Data Science Fundamentals",
        issued_by="Data Academy",
        completion_date="2024-06-01",
    )
    with open(file_path, "rb") as f:
        header = f.read(4)
    assert header == b"%PDF"


def test_generate_certificate_filename_uses_cert_id(tmp_path, monkeypatch):
    monkeypatch.setattr("app.certificate_generator.CERTIFICATES_DIR", str(tmp_path))
    file_path = generate_certificate_pdf(
        job_id="job-3",
        cert_id="unique-cert-xyz",
        recipient_name="Carol White",
        recipient_email="carol@example.com",
        event_name="Cloud Computing",
        issued_by="Cloud Institute",
        completion_date="2024-07-01",
    )
    assert "unique-cert-xyz" in file_path


def test_generate_certificate_with_long_event_name(tmp_path, monkeypatch):
    monkeypatch.setattr("app.certificate_generator.CERTIFICATES_DIR", str(tmp_path))
    long_name = "Advanced Python Programming Bootcamp for Software Engineers and Data Scientists"
    file_path = generate_certificate_pdf(
        job_id="job-4",
        cert_id="cert-4",
        recipient_name="Dan Brown",
        recipient_email="dan@example.com",
        event_name=long_name,
        issued_by="Institute",
        completion_date="2024-08-01",
    )
    assert os.path.exists(file_path)
