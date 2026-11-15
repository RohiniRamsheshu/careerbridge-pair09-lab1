from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.app.auth import get_authenticated_user
from backend.app.database import get_connection
from backend.app.services import application_service
from backend.app import config
from backend.app.events.outbox import enqueue_event, make_event

router = APIRouter(prefix="/applications", tags=["Applications"])

RESUME_DIR = Path("backend/uploads/resumes")
RESUME_DIR.mkdir(parents=True, exist_ok=True)
MAX_RESUME_SIZE = 5 * 1024 * 1024
ALLOWED_STATUSES = {"Reviewed", "Declined"}


def require_role(user, role):
    if user["role"] != role:
        raise HTTPException(status_code=403, detail="Forbidden")


def run_query(sql, params=(), fetch="all", commit=False):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        if commit:
            connection.commit()
            return cursor.lastrowid
        if fetch == "one":
            return cursor.fetchone()
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def _safe_resume_path(raw_path):
    """Validate a stored resume without exposing its filesystem location."""
    if not raw_path:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_path = Path(raw_path).resolve()
    resume_root = RESUME_DIR.resolve()
    try:
        resume_path.relative_to(resume_root)
    except ValueError:
        raise HTTPException(status_code=404, detail="Resume not found")

    if resume_path.suffix.lower() != ".pdf" or not resume_path.is_file():
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        with resume_path.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                raise HTTPException(status_code=404, detail="Resume not found")
    except OSError:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume_path


@router.post("/resume", status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    user=Depends(get_authenticated_user),
):
    require_role(user, "student")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are allowed")

    content = await file.read(MAX_RESUME_SIZE + 1)

    if len(content) > MAX_RESUME_SIZE:
        raise HTTPException(status_code=413, detail="Resume must be 5 MB or smaller")

    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Invalid PDF file")

    filename = f"{user['id']}_{uuid4().hex}.pdf"
    destination = RESUME_DIR / filename
    destination.write_bytes(content)

    return {
        "resume_path": str(destination).replace("\\", "/"),
        "message": "Resume uploaded",
    }


@router.get("/resume")
def list_resumes(user=Depends(get_authenticated_user)):
    require_role(user, "student")

    files = sorted(
        RESUME_DIR.glob(f"{user['id']}_*.pdf"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    return [
        {
            "resume_path": str(path).replace("\\", "/"),
            "filename": path.name,
        }
        for path in files
    ]


class ApplyRequest(BaseModel):
    resume_path: str


@router.post("/{job_id}/apply", status_code=201)
def apply_to_job(
    job_id: int,
    request: ApplyRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "student")

    resume_path = Path(request.resume_path).resolve()
    resume_root = RESUME_DIR.resolve()

    if resume_root not in resume_path.parents:
        raise HTTPException(status_code=400, detail="Invalid resume path")

    if not resume_path.is_file():
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume_path.name.startswith(f"{user['id']}_"):
        raise HTTPException(status_code=403, detail="Resume does not belong to you")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM jobs WHERE id = %s AND deadline >= CURDATE()",
            (job_id,),
        )
        job = cursor.fetchone()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found or deadline passed")

        cursor.execute(
            """
            SELECT id FROM applications
            WHERE job_id = %s AND student_user_id = %s
            """,
            (job_id, user["id"]),
        )

        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Already applied")

        cursor.execute(
            """
            INSERT INTO applications
            (job_id, student_user_id, resume_path, status)
            VALUES (%s, %s, %s, 'Pending')
            """,
            (
                job_id,
                user["id"],
                str(resume_path).replace("\\", "/"),
            ),
        )

        application_id = cursor.lastrowid
        if config.KAFKA_ENABLED:
            enqueue_event(
                cursor,
                make_event(
                    "application.created", application_id, "application",
                    {"job_id": job_id, "student_user_id": user["id"], "status": "Pending"},
                ),
            )
        connection.commit()

        return {
            "id": application_id,
            "message": "Application submitted",
        }

    finally:
        cursor.close()
        connection.close()


@router.get("/student")
def student_applications(user=Depends(get_authenticated_user)):
    require_role(user, "student")
    return application_service.list_for_student(run_query, user["id"])


@router.get("/company/jobs/{job_id}/applicants")
def get_applicants(
    job_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")

    job, applicants = application_service.owned_applicants(run_query, job_id, user["id"])
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return applicants


@router.get("/company/jobs/{job_id}/applicants/{application_id}/profile")
def get_applicant_profile(
    job_id: int,
    application_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")

    profile = application_service.applicant_profile(
        run_query, job_id, application_id, user["id"]
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Applicant profile not found")
    return profile


@router.get("/company/jobs/{job_id}/applicants/{application_id}/resume")
def preview_applicant_resume(
    job_id: int,
    application_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")

    application = application_service.applicant_resume(
        run_query, job_id, application_id, user["id"]
    )
    if not application:
        raise HTTPException(status_code=404, detail="Applicant resume not found")

    resume_path = _safe_resume_path(application.get("resume_path"))
    return FileResponse(
        str(resume_path),
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="resume.pdf"'},
    )


class ApplicationStatusRequest(BaseModel):
    status: str


@router.patch("/company/jobs/{job_id}/applicants/{application_id}/status")
def update_application_status(
    job_id: int,
    application_id: int,
    request: ApplicationStatusRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")

    if request.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Status must be Reviewed or Declined",
        )

    if config.KAFKA_ENABLED:
        updated_application_id = application_service.update_status_with_outbox(
            get_connection, job_id, application_id, user["id"], request.status,
            enqueue_event, make_event,
        )
    else:
        updated_application_id = application_service.update_status(
            run_query, job_id, application_id, user["id"], request.status
        )
    if not updated_application_id:
        raise HTTPException(status_code=404, detail="Application not found")

    return {"message": "Application status updated"}
