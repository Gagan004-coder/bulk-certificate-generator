from app.database import SessionLocal
from app.models import Job, Certificate, JobStatus, CertificateStatus
from app.certificate_generator import generate_certificate_pdf_bytes


def process_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.processing
        db.commit()

        certificates = db.query(Certificate).filter(Certificate.job_id == job_id).all()

        succeeded = 0
        failed = 0

        for cert in certificates:
            try:
                pdf_bytes = generate_certificate_pdf_bytes(
                    cert_id=cert.id,
                    recipient_name=cert.recipient_name,
                    recipient_email=cert.recipient_email,
                    event_name=job.event_name,
                    issued_by=job.issued_by,
                    completion_date=cert.completion_date,
                )
                cert.status = CertificateStatus.success
                cert.file_data = pdf_bytes
                succeeded += 1
            except Exception as exc:
                cert.status = CertificateStatus.failed
                cert.error_message = str(exc)
                failed += 1

            db.commit()

        job.succeeded = succeeded
        job.failed = failed
        job.status = JobStatus.completed
        db.commit()

    except Exception as exc:
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.failed
            db.commit()
        raise exc
    finally:
        db.close()
