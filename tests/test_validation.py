import pytest
from tests.conftest import VALID_PAYLOAD


def test_missing_event_name(client):
    payload = {**VALID_PAYLOAD, "event_name": ""}
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 422


def test_missing_issued_by(client):
    payload = {**VALID_PAYLOAD, "issued_by": ""}
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 422


def test_empty_recipients(client):
    payload = {**VALID_PAYLOAD, "recipients": []}
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 422


def test_invalid_email(client):
    payload = {
        **VALID_PAYLOAD,
        "recipients": [
            {"name": "Alice", "email": "not-an-email", "completion_date": "2024-05-01"}
        ],
    }
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 422


def test_blank_recipient_name(client):
    payload = {
        **VALID_PAYLOAD,
        "recipients": [
            {"name": "   ", "email": "alice@example.com", "completion_date": "2024-05-01"}
        ],
    }
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 422


def test_invalid_date_format(client):
    payload = {
        **VALID_PAYLOAD,
        "recipients": [
            {"name": "Alice", "email": "alice@example.com", "completion_date": "not-a-date"}
        ],
    }
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 422


def test_missing_required_fields(client):
    resp = client.post("/api/v1/jobs", json={})
    assert resp.status_code == 422
