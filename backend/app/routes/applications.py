
import os
from pathlib import Path
from backend.app.database import get_connection
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.app.auth import get_authenticated_user

router = APIRouter(prefix="/applications", tags=["Applications"])

RESUME_DIR = Path("backend/uploads/resumes")
RESUME_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    user=Depends(get_authenticated_user),
):
    if user["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Only student accounts can upload resumes",
        )

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are allowed",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="File is empty")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Resume must be 5 MB or smaller",
        )

    if not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file",
        )

    filename = f"{user['id']}_{uuid4().hex}.pdf"
    file_path = RESUME_DIR / filename

    with open(file_path, "wb") as resume:
        resume.write(contents)

    return {
        "message": "Resume uploaded successfully",
        "resume_path": str(file_path).replace("\\", "/"),
    }

@router.post("/{job_id}/apply")
def apply_to_job(
    job_id: int,
    user=Depends(get_authenticated_user),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only student accounts can apply")

    resume_files = list(RESUME_DIR.glob(f"{user['id']}_*.pdf"))

    if not resume_files:
        raise HTTPException(status_code=400, detail="Upload a resume before applying")

    resume_path = str(resume_files[-1]).replace("\\", "/")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM jobs WHERE id = %s", (job_id,))
        job = cursor.fetchone()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        cursor.execute(
            "SELECT id FROM applications WHERE job_id = %s AND student_user_id = %s",
            (job_id, user["id"]),
        )

        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Already applied to this job")

        cursor.execute(
            """
            INSERT INTO applications (job_id, student_user_id, resume_path, status)
            VALUES (%s, %s, %s, %s)
            """,
            (job_id, user["id"], resume_path, "Pending"),
        )

        application_id = cursor.lastrowid
        connection.commit()

        return {
            "message": "Application submitted successfully",
            "application_id": application_id,
            "job_id": job_id,
            "status": "Pending",
        }

    finally:
        cursor.close()
        connection.close()

@router.get("/company/jobs/{job_id}/applicants")
def get_job_applicants(
    job_id: int,
    user=Depends(get_authenticated_user),
):
    if user["role"] != "company":
        raise HTTPException(status_code=403, detail="Company access required")

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM jobs WHERE id = %s AND company_user_id = %s",
            (job_id, user["id"]),
        )

        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job not found")

        cursor.execute(
            """
            SELECT
                a.id AS application_id,
                a.job_id,
                a.student_user_id,
                u.name,
                u.email,
                a.resume_path,
                a.status,
                a.applied_at,
                sp.college,
                sp.degree,
                sp.major,
                sp.graduation_year,
                sp.cgpa,
                sp.experience
            FROM applications a
            JOIN users u ON u.id = a.student_user_id
            LEFT JOIN student_profiles sp ON sp.user_id = a.student_user_id
            WHERE a.job_id = %s
            ORDER BY a.applied_at DESC, a.id DESC
            """,
            (job_id,),
        )

        applicants = cursor.fetchall()
        return {"applicants": applicants, "count": len(applicants)}

    finally:
        cursor.close()
        connection.close()
