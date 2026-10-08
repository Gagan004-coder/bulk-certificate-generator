import pytest
from unittest.mock import patch
from app.tasks import process_job
from app.models import Job, Certificate, JobStatus, CertificateStatus
from tests.conftest import TestingSessionLocal

FAKE_PDF = b"%PDF-1.4 fake content"


def make_job(recipients=None, event_name="Test Event", issued_by="Org"):
    if recipients is None:
        recipients = [
            ("Alice", "alice@example.com", "2024-05-01"),
            ("Bob", "bob@example.com", "2024-05-01"),
        ]
    session = TestingSessionLocal()
    job = Job(event_name=event_name, issued_by=issued_by, total=len(recipients))
    session.add(job)
    session.flush()
    for name, email, date in recipients:
        cert = Certificate(
            job_id=job.id,
            recipient_name=name,
            recipient_email=email,
            completion_date=date,
        )
        session.add(cert)
    session.commit()
    job_id = job.id
    session.close()
    return job_id


def get_job(job_id):
    s = TestingSessionLocal()
    job = s.query(Job).filter(Job.id == job_id).first()
    s.close()
    return job


def get_certs(job_id):
    s = TestingSessionLocal()
    certs = s.query(Certificate).filter(Certificate.job_id == job_id).all()
    s.close()
    return certs


def test_process_job_completes_successfully():
    job_id = make_job()

    with patch("app.tasks.SessionLocal", side_effect=TestingSessionLocal), \
         patch("app.tasks.generate_certificate_pdf_bytes", return_value=FAKE_PDF):
        process_job(job_id)

    job = get_job(job_id)
    assert job.status == JobStatus.completed
    assert job.succeeded == 2
    assert job.failed == 0


def test_process_job_marks_as_completed():
    job_id = make_job()

    with patch("app.tasks.SessionLocal", side_effect=TestingSessionLocal), \
         patch("app.tasks.generate_certificate_pdf_bytes", return_value=FAKE_PDF):
        process_job(job_id)

    job = get_job(job_id)
    assert job.status == JobStatus.completed


def test_process_job_one_failure_does_not_block_others():
    job_id = make_job(recipients=[
        ("Alice", "alice@example.com", "2024-05-01"),
        ("Bob", "bob@example.com", "2024-05-01"),
        ("Carol", "carol@example.com", "2024-05-01"),
    ])

    call_count = 0

    def side_effect(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise RuntimeError("Simulated generation failure")
        return FAKE_PDF

    with patch("app.tasks.SessionLocal", side_effect=TestingSessionLocal), \
         patch("app.tasks.generate_certificate_pdf_bytes", side_effect=side_effect):
        process_job(job_id)

    job = get_job(job_id)
    assert job.succeeded == 2
    assert job.failed == 1
    assert job.status == JobStatus.completed

    certs = get_certs(job_id)
    failed_certs = [c for c in certs if c.status == CertificateStatus.failed]
    assert len(failed_certs) == 1
    assert "Simulated generation failure" in failed_certs[0].error_message


def test_process_job_records_error_message_on_failure():
    job_id = make_job(recipients=[("Alice", "alice@example.com", "2024-05-01")])

    with patch("app.tasks.SessionLocal", side_effect=TestingSessionLocal), \
         patch("app.tasks.generate_certificate_pdf_bytes", side_effect=Exception("disk full")):
        process_job(job_id)

    certs = get_certs(job_id)
    assert certs[0].status == CertificateStatus.failed
    assert "disk full" in certs[0].error_message


def test_process_job_nonexistent_job_id():
    with patch("app.tasks.SessionLocal", side_effect=TestingSessionLocal):
        result = process_job("nonexistent-job-id")
    assert result is None


def test_process_job_stores_pdf_bytes():
    job_id = make_job(recipients=[("Alice", "alice@example.com", "2024-05-01")])

    with patch("app.tasks.SessionLocal", side_effect=TestingSessionLocal), \
         patch("app.tasks.generate_certificate_pdf_bytes", return_value=FAKE_PDF):
        process_job(job_id)

    certs = get_certs(job_id)
    assert certs[0].file_data == FAKE_PDF
