import pytest
from app.certificate_generator import generate_certificate_pdf_bytes


def test_generate_certificate_returns_bytes():
    result = generate_certificate_pdf_bytes(
        cert_id="cert-1",
        recipient_name="Alice Smith",
        recipient_email="alice@example.com",
        event_name="Python Bootcamp",
        issued_by="Tech Academy",
        completion_date="2024-05-01",
    )
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_generate_certificate_is_valid_pdf():
    result = generate_certificate_pdf_bytes(
        cert_id="cert-2",
        recipient_name="Bob Jones",
        recipient_email="bob@example.com",
        event_name="Data Science Fundamentals",
        issued_by="Data Academy",
        completion_date="2024-06-01",
    )
    assert result[:4] == b"%PDF"


def test_generate_certificate_with_long_event_name():
    long_name = "Advanced Python Programming Bootcamp for Software Engineers and Data Scientists"
    result = generate_certificate_pdf_bytes(
        cert_id="cert-3",
        recipient_name="Carol White",
        recipient_email="carol@example.com",
        event_name=long_name,
        issued_by="Institute",
        completion_date="2024-07-01",
    )
    assert isinstance(result, bytes)
    assert result[:4] == b"%PDF"


def test_generate_certificate_different_calls_produce_different_content():
    result1 = generate_certificate_pdf_bytes(
        cert_id="cert-4",
        recipient_name="Alice",
        recipient_email="alice@example.com",
        event_name="Event A",
        issued_by="Org",
        completion_date="2024-05-01",
    )
    result2 = generate_certificate_pdf_bytes(
        cert_id="cert-5",
        recipient_name="Bob",
        recipient_email="bob@example.com",
        event_name="Event B",
        issued_by="Org",
        completion_date="2024-05-01",
    )
    assert result1 != result2
