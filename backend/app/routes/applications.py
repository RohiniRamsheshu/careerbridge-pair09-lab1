from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

from backend.app.auth import get_authenticated_user
from backend.app.database import get_connection

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

        connection.commit()

        return {
            "id": cursor.lastrowid,
            "message": "Application submitted",
        }

    finally:
        cursor.close()
        connection.close()


@router.get("/student")
def student_applications(user=Depends(get_authenticated_user)):
    require_role(user, "student")

    return run_query(
        """
        SELECT a.id, a.job_id, a.resume_path, a.status, a.applied_at,
               j.title, j.company_user_id, c.company_name
        FROM applications a
        JOIN jobs j ON j.id = a.job_id
        JOIN company_profiles c ON c.user_id = j.company_user_id
        WHERE a.student_user_id = %s
        ORDER BY a.applied_at DESC
        """,
        (user["id"],),
    )


@router.get("/company/jobs/{job_id}/applicants")
def get_applicants(
    job_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")

    job = run_query(
        """
        SELECT id FROM jobs
        WHERE id = %s AND company_user_id = %s
        """,
        (job_id, user["id"]),
        fetch="one",
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return run_query(
        """
        SELECT a.id AS application_id, a.status, a.applied_at,
               a.resume_path, u.id AS student_id, u.name, u.email,
               sp.college, sp.degree, sp.major, sp.graduation_year,
               sp.cgpa, sp.experience
        FROM applications a
        JOIN users u ON u.id = a.student_user_id
        LEFT JOIN student_profiles sp ON sp.user_id = u.id
        WHERE a.job_id = %s
        ORDER BY a.applied_at DESC
        """,
        (job_id,),
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

    application = run_query(
        """
        SELECT a.id
        FROM applications a
        JOIN jobs j ON j.id = a.job_id
        WHERE a.id = %s
          AND a.job_id = %s
          AND j.company_user_id = %s
        """,
        (application_id, job_id, user["id"]),
        fetch="one",
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    run_query(
        "UPDATE applications SET status = %s WHERE id = %s",
        (request.status, application_id),
        commit=True,
    )

    return {"message": "Application status updated"}