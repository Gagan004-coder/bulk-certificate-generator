from datetime import date
from pydantic import BaseModel, EmailStr, field_validator
from app.models import JobStatus, CertificateStatus


class RecipientIn(BaseModel):
    name: str
    email: EmailStr
    completion_date: date

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()


class JobCreateRequest(BaseModel):
    event_name: str
    issued_by: str
    recipients: list[RecipientIn]

    @field_validator("event_name", "issued_by")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field must not be blank")
        return v.strip()

    @field_validator("recipients")
    @classmethod
    def at_least_one(cls, v: list) -> list:
        if not v:
            raise ValueError("recipients list must not be empty")
        return v


class CertificateOut(BaseModel):
    id: str
    job_id: str
    recipient_name: str
    recipient_email: str
    completion_date: str
    status: CertificateStatus
    error_message: str | None

    model_config = {"from_attributes": True}


class JobOut(BaseModel):
    id: str
    event_name: str
    issued_by: str
    status: JobStatus
    total: int
    succeeded: int
    failed: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, job):
        return cls(
            id=job.id,
            event_name=job.event_name,
            issued_by=job.issued_by,
            status=job.status,
            total=job.total,
            succeeded=job.succeeded,
            failed=job.failed,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )


class JobDetailOut(JobOut):
    certificates: list[CertificateOut] = []
