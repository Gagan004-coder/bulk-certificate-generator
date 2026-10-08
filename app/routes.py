from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, Certificate, JobStatus, CertificateStatus
from app.schemas import JobCreateRequest, JobOut, JobDetailOut, CertificateOut
from app.tasks import process_job

router = APIRouter(prefix="/api/v1", tags=["certificates"])


@router.post("/jobs", response_model=JobOut, status_code=202)
def create_job(payload: JobCreateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job = Job(
        event_name=payload.event_name,
        issued_by=payload.issued_by,
        total=len(payload.recipients),
        status=JobStatus.pending,
    )
    db.add(job)
    db.flush()

    for recipient in payload.recipients:
        cert = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=str(recipient.email),
            completion_date=str(recipient.completion_date),
        )
        db.add(cert)

    db.commit()
    db.refresh(job)

    background_tasks.add_task(process_job, job.id)

    return JobOut.from_orm_model(job)


@router.get("/jobs/{job_id}", response_model=JobDetailOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobDetailOut(
        id=job.id,
        event_name=job.event_name,
        issued_by=job.issued_by,
        status=job.status,
        total=job.total,
        succeeded=job.succeeded,
        failed=job.failed,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        certificates=[CertificateOut.model_validate(c) for c in job.certificates],
    )


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return [JobOut.from_orm_model(j) for j in jobs]


@router.get("/jobs/{job_id}/certificates", response_model=list[CertificateOut])
def list_certificates(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return [CertificateOut.model_validate(c) for c in job.certificates]


@router.get("/certificates/{cert_id}/download")
def download_certificate(cert_id: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if cert.status != CertificateStatus.success or not cert.file_data:
        raise HTTPException(status_code=409, detail="Certificate is not ready yet")

    filename = f"certificate_{cert.recipient_name.replace(' ', '_')}.pdf"
    return Response(
        content=cert.file_data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
