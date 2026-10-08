# Bulk Certificate Generator

A production-ready, scalable backend API for generating and distributing beautiful PDF certificates for large numbers of recipients. Built with **FastAPI**, **PostgreSQL**, and **ReportLab**.

---

## 🌐 Live Deployment & Links

- **Live Base API:** [https://bulk-cert-api.onrender.com](https://bulk-cert-api.onrender.com)
- **Interactive Swagger Docs:** [https://bulk-cert-api.onrender.com/docs](https://bulk-cert-api.onrender.com/docs)
- **ReDoc Documentation:** [https://bulk-cert-api.onrender.com/redoc](https://bulk-cert-api.onrender.com/redoc)
- **GitHub Repository:** [https://github.com/Gagan004-coder/bulk-certificate-generator](https://github.com/Gagan004-coder/bulk-certificate-generator)

---

## ⚡ Tech Stack

| Layer | Technology | Description |
|---|---|---|
| **Framework** | FastAPI | High-performance asynchronous REST API framework |
| **Async Processing** | FastAPI `BackgroundTasks` | Non-blocking background certificate generation |
| **Database & ORM** | PostgreSQL & SQLAlchemy 2.0 | Relational database storing job metadata & PDF byte blobs (`BYTEA`) |
| **PDF Engine** | ReportLab | Programmatic generation of vector PDF certificates |
| **Validation** | Pydantic v2 | Strict schema validation and email formatting |
| **Testing** | Pytest & HTTPX TestClient | Comprehensive test suite (30/30 tests passing) |
| **Deployment** | Render (Free Tier Blueprint) | Automated web + managed PostgreSQL cloud deployment |

---

## 📂 Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py                 # Environment-based configuration
│   ├── database.py               # SQLAlchemy engine & session factory
│   ├── models.py                 # ORM models (Job, Certificate, Enums)
│   ├── schemas.py                # Pydantic request/response models
│   ├── certificate_generator.py  # ReportLab PDF design and rendering
│   ├── tasks.py                  # Background job processing logic
│   ├── routes.py                 # API endpoints
│   └── main.py                   # FastAPI application entrypoint
├── tests/
│   ├── conftest.py               # Test fixtures & SQLite testing DB
│   ├── test_jobs.py              # Job creation and retrieval tests
│   ├── test_validation.py        # Input validation & bad payload tests
│   ├── test_certificate_generator.py # PDF generation unit tests
│   ├── test_tasks.py             # Background task execution tests
│   ├── test_status.py            # Status polling and counters tests
│   └── test_download.py          # PDF streaming & download tests
├── requirements.txt              # Production and test dependencies
├── render.yaml                   # Infrastructure-as-code deployment blueprint
├── .env.example                  # Environment configuration template
└── README.md
```

---

## 🚀 Getting Started Locally

### Prerequisites

- Python 3.11+
- SQLite (included with Python) or PostgreSQL

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/Gagan004-coder/bulk-certificate-generator.git
cd bulk-certificate-generator
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Default `.env` for local development uses SQLite:
```env
DATABASE_URL=sqlite:///./certs.db
```

### 3. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Base: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`

---

## 🧪 Running Tests

Execute the full suite of 30 unit and integration tests:

```bash
pytest tests/ -v
```

All tests run against an in-memory/isolated SQLite test database with complete endpoint, validation, task processing, and PDF generation coverage.

---

## 📖 API Reference

### 1. Health Check
```http
GET /health
```
**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

---

### 2. Submit Certificate Generation Job
```http
POST /api/v1/jobs
```

**Request Body:**
```json
{
  "event_name": "Full Stack Engineering Bootcamp 2026",
  "issued_by": "Global Tech Academy",
  "recipients": [
    {
      "name": "Jane Doe",
      "email": "jane.doe@example.com",
      "completion_date": "2026-05-15"
    },
    {
      "name": "John Smith",
      "email": "john.smith@example.com",
      "completion_date": "2026-05-15"
    }
  ]
}
```

**Response (202 Accepted):**
```json
{
  "id": "e93db940-0853-4712-9cbb-c1550cbb64b5",
  "event_name": "Full Stack Engineering Bootcamp 2026",
  "issued_by": "Global Tech Academy",
  "status": "pending",
  "total": 2,
  "succeeded": 0,
  "failed": 0,
  "created_at": "2026-10-08T01:00:00Z",
  "updated_at": "2026-10-08T01:00:00Z"
}
```

---

### 3. Track Job Status
```http
GET /api/v1/jobs/{job_id}
```

**Response (200 OK):**
```json
{
  "id": "e93db940-0853-4712-9cbb-c1550cbb64b5",
  "event_name": "Full Stack Engineering Bootcamp 2026",
  "issued_by": "Global Tech Academy",
  "status": "completed",
  "total": 2,
  "succeeded": 2,
  "failed": 0,
  "created_at": "2026-10-08T01:00:00Z",
  "updated_at": "2026-10-08T01:00:05Z",
  "certificates": [
    {
      "id": "c1a2b3c4-0000-0000-0000-000000000001",
      "recipient_name": "Jane Doe",
      "recipient_email": "jane.doe@example.com",
      "completion_date": "2026-05-15",
      "status": "success",
      "download_url": "/api/v1/certificates/c1a2b3c4-0000-0000-0000-000000000001/download",
      "error_message": null
    }
  ]
}
```

---

### 4. List All Jobs
```http
GET /api/v1/jobs?skip=0&limit=20
```

---

### 5. Download Certificate PDF
```http
GET /api/v1/certificates/{certificate_id}/download
```

- Returns `200 OK` with binary `application/pdf` stream and `Content-Disposition: attachment; filename="certificate_<id>.pdf"`.
- Returns `409 Conflict` if the certificate is still pending or generation failed.
- Returns `404 Not Found` if the certificate ID does not exist.

---

## 🏛️ Architectural & Design Decisions

### 1. Asynchronous Background Generation
- Immediate response with `202 Accepted` returning the unique `job_id`.
- Long-running PDF rendering is offloaded to background task execution, keeping request/response loops lightweight and responsive.

### 2. Failure Isolation
- Each recipient's certificate generation is wrapped in an isolated exception handler.
- If one recipient fails (e.g. malformed data), the specific certificate is marked `failed` with its error message recorded, while all other valid certificates are generated successfully.
- The parent job transitions to `completed` once all recipients are processed.

### 3. Direct Binary Storage in PostgreSQL (`BYTEA`)
- Generated PDF bytes are stored directly in the database (`BYTEA` column).
- Eliminates the need for local filesystem persistent disks or expensive external S3 buckets, allowing reliable, zero-config deployment on free tiers like Render.

### 4. Professional Certificate Aesthetic
- Generated dynamically via ReportLab with A4 Landscape dimensions.
- Features double gold borders, ornate corner ornaments, clean serif typography, issue metadata, and a unique tracking ID at the bottom for authenticity.
