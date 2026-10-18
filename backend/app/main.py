
import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal

import bcrypt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr, Field

from backend.app.database import get_connection
from backend.app.auth import get_authenticated_user

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is missing from .env")

app = FastAPI(
    title="Handshake Lab 1 API",
    description="Backend API for the Handshake student and job platform.",
    version="0.1.0",
)

security = HTTPBearer()

JobCategory = Literal[
    "full time",
    "part time",
    "on campus",
    "internship",
]


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["student", "company"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class JobCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    deadline: date
    location: str = Field(min_length=1, max_length=200)
    salary: Decimal | None = Field(default=None, ge=0)
    description: str = Field(min_length=1)
    category: JobCategory
    is_remote: bool = False


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/database")
def database_health():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE()")
        database_name = cursor.fetchone()[0]
        cursor.close()

        return {
            "status": "connected",
            "database": database_name,
        }

    finally:
        connection.close()


@app.post("/auth/register", status_code=201)
def register_user(data: RegisterRequest):
    name = data.name.strip()
    email = str(data.email).strip().lower()

    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters",
        )

    password_hash = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, password_hash, data.role),
        )

        user_id = cursor.lastrowid
        connection.commit()

        return {
            "id": user_id,
            "name": name,
            "email": email,
            "role": data.role,
        }

    except Exception as error:
        connection.rollback()

        if getattr(error, "errno", None) == 1062:
            raise HTTPException(
                status_code=409,
                detail="Email is already registered",
            )

        raise

    finally:
        connection.close()


@app.post("/auth/login")
def login_user(data: LoginRequest):
    email = str(data.email).strip().lower()
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, name, email, password_hash, role
            FROM users
            WHERE email = %s
            """,
            (email,),
        )
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(
            data.password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=JWT_EXPIRE_MINUTES
        )

        token = jwt.encode(
            {
                "sub": str(user["id"]),
                "exp": expires_at,
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM,
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            },
        }

    finally:
        connection.close()


@app.get("/auth/me")
def get_current_user(user=Depends(get_authenticated_user)):
    return user


@app.post("/jobs", status_code=201)
def create_job(
    data: JobCreateRequest,
    user=Depends(get_authenticated_user),
):
    if user["role"] != "company":
        raise HTTPException(
            status_code=403,
            detail="Only company accounts can create jobs",
        )

    if data.deadline < date.today():
        raise HTTPException(
            status_code=400,
            detail="Deadline cannot be in the past",
        )

    title = data.title.strip()
    location = data.location.strip()
    description = data.description.strip()

    if not title or not location or not description:
        raise HTTPException(
            status_code=400,
            detail="Title, location, and description are required",
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT user_id FROM company_profiles WHERE user_id = %s",
            (user["id"],),
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Create a company profile before posting jobs",
            )

        cursor.execute(
            """
            INSERT INTO jobs (
                company_user_id,
                title,
                posting_date,
                deadline,
                location,
                salary,
                description,
                category,
                is_remote
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user["id"],
                title,
                date.today(),
                data.deadline,
                location,
                data.salary,
                description,
                data.category,
                data.is_remote,
            ),
        )

        job_id = cursor.lastrowid
        connection.commit()

        return {
            "id": job_id,
            "company_user_id": user["id"],
            "title": title,
            "posting_date": date.today(),
            "deadline": data.deadline,
            "location": location,
            "salary": data.salary,
            "description": description,
            "category": data.category,
            "is_remote": data.is_remote,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


@app.get("/jobs")
def browse_jobs(
    location: str | None = Query(default=None, max_length=200),
    category: JobCategory | None = None,
    user=Depends(get_authenticated_user),
):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        sql = """
            SELECT
                j.id,
                j.company_user_id,
                cp.company_name,
                j.title,
                j.posting_date,
                j.deadline,
                j.location,
                j.salary,
                j.description,
                j.category,
                j.is_remote
            FROM jobs j
            JOIN company_profiles cp
                ON cp.user_id = j.company_user_id
            WHERE j.deadline >= %s
        """

        params = [date.today()]

        if location and location.strip():
            sql += " AND j.location LIKE %s"
            params.append("%" + location.strip() + "%")

        if category:
            sql += " AND j.category = %s"
            params.append(category)

        sql += " ORDER BY j.posting_date DESC, j.id DESC"

        cursor.execute(sql, tuple(params))
        jobs = cursor.fetchall()

        return {"jobs": jobs, "count": len(jobs)}

    finally:
        connection.close()


from backend.app.routes.applications import router as applications_router

app.include_router(applications_router)
@app.get("/company/jobs")
def get_company_jobs(user=Depends(get_authenticated_user)):
    if user["role"] != "company":
        raise HTTPException(status_code=403, detail="Company access required")

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                j.id,
                j.title,
                j.posting_date,
                j.deadline,
                j.location,
                j.salary,
                j.description,
                j.category,
                j.is_remote,
                COUNT(a.id) AS application_count
            FROM jobs j
            LEFT JOIN applications a ON a.job_id = j.id
            WHERE j.company_user_id = %s
            GROUP BY
                j.id,
                j.title,
                j.posting_date,
                j.deadline,
                j.location,
                j.salary,
                j.description,
                j.category,
                j.is_remote
            ORDER BY j.posting_date DESC, j.id DESC
            """,
            (user["id"],),
        )
        jobs = cursor.fetchall()
        return {"jobs": jobs, "count": len(jobs)}
    finally:
        connection.close()
