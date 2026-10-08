# Bulk Certificate Generator

A production-ready backend API for generating PDF certificates for large numbers of recipients. Built with FastAPI, Celery, Redis, and PostgreSQL.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Background Workers | Celery |
| Message Broker / Result Backend | Redis |
| Database | PostgreSQL (SQLite for local/tests) |
| PDF Generation | ReportLab |
| Deployment | Render |

---

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py               # Env-based configuration
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models.py               # ORM models: Job, Certificate
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── certificate_generator.py # ReportLab PDF generation
│   ├── celery_app.py           # Celery app instance + config
│   ├── tasks.py                # Celery tasks
│   ├── routes.py               # FastAPI route handlers
│   └── main.py                 # App entrypoint
├── tests/
│   ├── conftest.py
│   ├── test_jobs.py
│   ├── test_validation.py
│   ├── test_certificate_generator.py
│   ├── test_tasks.py
│   ├── test_status.py
│   └── test_download.py
├── requirements.txt
├── render.yaml
├── .env.example
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (or use SQLite for local dev)
- Redis

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
DATABASE_URL=postgresql://user:password@localhost:5432/certdb
REDIS_URL=redis://localhost:6379/0
CERTIFICATES_DIR=certificates
SECRET_KEY=your-secret-key-here
```

For quick local testing without PostgreSQL, use SQLite:

```
DATABASE_URL=sqlite:///./certs.db
```

---

## Running the Application

You need **two** processes running simultaneously.

### Terminal 1 — API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 — Celery Worker

```bash
celery -A app.tasks worker --loglevel=info
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

## Running Tests

Tests use SQLite and do not require Redis or a running Celery worker (tasks are tested directly with mocks).

```bash
pytest tests/ -v
```

---

## API Reference

### Create a Certificate Generation Job

```
POST /api/v1/jobs
```

**Request body:**

```json
{
  "event_name": "Python Bootcamp 2024",
  "issued_by": "Tech Academy",
  "recipients": [
    {
      "name": "Alice Smith",
      "email": "alice@example.com",
      "completion_date": "2024-05-01"
    },
    {
      "name": "Bob Jones",
      "email": "bob@example.com",
      "completion_date": "2024-05-01"
    }
  ]
}
```

**Response (202 Accepted):**

```json
{
  "id": "uuid",
  "event_name": "Python Bootcamp 2024",
  "issued_by": "Tech Academy",
  "status": "pending",
  "total": 2,
  "succeeded": 0,
  "failed": 0,
  "created_at": "...",
  "updated_at": "..."
}
```

---

### Check Job Status

```
GET /api/v1/jobs/{job_id}
```

Returns the job with its full list of certificates and their individual statuses.

**Job status values:** `pending` → `processing` → `completed` | `failed`

**Certificate status values:** `pending` → `success` | `failed`

---

### List All Jobs

```
GET /api/v1/jobs?skip=0&limit=20
```

---

### List Certificates for a Job

```
GET /api/v1/jobs/{job_id}/certificates
```

---

### Download a Certificate PDF

```
GET /api/v1/certificates/{cert_id}/download
```

Returns the PDF file directly (`application/pdf`).

Returns `409` if the certificate is not yet ready, `404` if it does not exist.

---

## Deployment on Render

The `render.yaml` blueprint provisions everything automatically:

1. **Web service** — FastAPI API
2. **Worker service** — Celery worker
3. **PostgreSQL database**
4. **Redis instance**
5. **Persistent disk** — for storing generated PDFs

### Steps

1. Push this repository to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Blueprint**.
3. Connect your GitHub repository.
4. Render detects `render.yaml` and creates all services.
5. Wait for the build to complete.
6. The API URL will be shown in the Render dashboard.

---

## Design Decisions

### Background Processing with Celery

Generation is handled asynchronously via Celery workers backed by Redis. The API returns `202 Accepted` immediately with the job ID, and the client polls `GET /api/v1/jobs/{job_id}` to track progress.

**Why Celery over `ThreadPoolExecutor`?**

- Celery workers are separate processes — they survive API restarts and can be scaled independently.
- On Render, the web service and worker are separate services, which is the industry-standard pattern.
- `task_acks_late=True` ensures tasks are not lost if a worker crashes mid-generation.
- This approach scales horizontally: add more worker instances to handle higher load.

### Isolated Certificate Failures

Each certificate is processed in a try/except block. A failure on one certificate (e.g., corrupted data, disk error) records the error message on that certificate row and increments the `failed` counter, but does not stop the rest of the job. The job always reaches a terminal state (`completed`).

### PDF Generation

ReportLab is used to generate landscape A4 PDFs with a professional design: gold double-border frame, decorative corner accents, styled typography using Times-Bold/Italic, and a footer with the certificate ID and recipient email for traceability.

### Database Design

Two tables: `jobs` (one per request) and `certificates` (one per recipient). This allows:
- Per-certificate status tracking
- Efficient queries for both bulk status and individual downloads
- Cascade deletes (deleting a job removes its certificates)

### Validation

Pydantic v2 schemas validate all inputs at the request boundary:
- `EmailStr` for email format
- `date` type for completion date
- Non-blank string validators for name, event name, issued_by
- At-least-one validator for recipients list
