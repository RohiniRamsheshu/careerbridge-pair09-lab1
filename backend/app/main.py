import os
import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import bcrypt
import mysql.connector
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from pydantic import BaseModel, EmailStr, Field

from backend.app.database import get_connection
from backend.app.auth import get_authenticated_user
from backend.app.routes.applications import router as applications_router
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing from the root .env file")

JWT_SECRET = JWT_SECRET_KEY
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

app = FastAPI(title="Handshake Lab 1 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router)


UPLOAD_DIR = Path("backend/uploads")
RESUME_DIR = UPLOAD_DIR / "resumes"
PROFILE_DIR = UPLOAD_DIR / "profiles"
RESUME_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

JOB_CATEGORIES = {"full time", "part time", "on campus", "internship"}
EVENT_TYPES = {"job", "event"}


def query_db(sql, params=(), fetch="all", commit=False):
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


def require_role(user, role):
    if user["role"] != role:
        raise HTTPException(status_code=403, detail="Forbidden")


def require_company_profile(user_id):
    profile = query_db(
        "SELECT user_id FROM company_profiles WHERE user_id = %s",
        (user_id,),
        fetch="one",
    )
    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Complete your company profile first",
        )


def require_student_profile(user_id):
    profile = query_db(
        "SELECT user_id FROM student_profiles WHERE user_id = %s",
        (user_id,),
        fetch="one",
    )
    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Complete your student profile first",
        )


def owned_job(job_id, company_id):
    job = query_db(
        """
        SELECT id, company_user_id, title
        FROM jobs
        WHERE id = %s
        """,
        (job_id,),
        fetch="one",
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["company_user_id"] != company_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return job


def owned_event(event_id, company_id):
    event = query_db(
        """
        SELECT id, company_user_id, name
        FROM events
        WHERE id = %s
        """,
        (event_id,),
        fetch="one",
    )
    if not event:

        raise HTTPException(status_code=404, detail="Event not found")
    if event["company_user_id"] != company_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return event


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/database")
def health_database():
    try:
        connection = get_connection()
        connection.close()
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8)
    role: str
    college: str | None = Field(default=None, max_length=200)
    company_name: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CompanyProfileRequest(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    description: str | None = None
    contact_information: str | None = None
    website: str | None = None


class StudentProfileRequest(BaseModel):
    date_of_birth: date | None = None
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    career_objective: str | None = None
    college: str = Field(min_length=1, max_length=200)
    degree: str | None = Field(default=None, max_length=150)
    major: str | None = Field(default=None, max_length=150)
    graduation_year: int | None = Field(default=None, ge=1900, le=2100)
    cgpa: Decimal | None = Field(default=None, ge=0, le=10)
    experience: str | None = None
    phone: str | None = Field(default=None, max_length=30)



class JobCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    deadline: date
    location: str = Field(min_length=1, max_length=200)
    salary: Decimal | None = Field(default=None, ge=0)
    description: str = Field(min_length=1)
    category: str
    is_remote: bool = False


class EventCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str
    event_date: date
    event_time: time
    location: str = Field(min_length=1, max_length=200)
    eligibility: str | None = None


class PreferencesRequest(BaseModel):
    preferred_categories: list[str] | None = None
    preferred_cities: list[str] | None = None
    preferred_skills: list[str] | None = None
    remote_only: bool = False
    minimum_salary: Decimal | None = Field(default=None, ge=0)


@app.post("/auth/register", status_code=201)
def register(request: RegisterRequest):
    role = request.role.strip().lower()
    email = str(request.email).strip().lower()

    if role not in {"student", "company"}:
        raise HTTPException(status_code=400, detail="Role must be student or company")

    if role == "student" and not request.college:
        raise HTTPException(status_code=400, detail="College is required for student registration")

    if role == "company" and (not request.company_name or not request.location):
        raise HTTPException(status_code=400, detail="Company name and location are required for company registration")

    password_hash = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (request.name.strip(), email, password_hash, role),
        )
        user_id = cursor.lastrowid

        if role == "student":
            cursor.execute(
                "INSERT INTO student_profiles (user_id, college) VALUES (%s, %s)",
                (user_id, request.college.strip()),
            )
        else:
            cursor.execute(

                "INSERT INTO company_profiles (user_id, company_name, location) VALUES (%s, %s, %s)",
                (user_id, request.company_name.strip(), request.location.strip()),
            )

        connection.commit()
    except mysql.connector.IntegrityError as exc:
        connection.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

    return {
        "id": user_id,
        "name": request.name.strip(),
        "email": email,
        "role": role,
        "message": "Account and profile created successfully",
    }


@app.post("/auth/login")
def login(request: LoginRequest):
    user = query_db(
        """
        SELECT id, name, email, password_hash, role
        FROM users
        WHERE email = %s
        """,
        (request.email.lower(),),
        fetch="one",
    )

    if not user or not bcrypt.checkpw(
        request.password.encode(),
        user["password_hash"].encode(),
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {
            "sub": str(user["id"]),
            "exp": datetime.utcnow() + timedelta(hours=1),
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


@app.get("/auth/me")
def me(user=Depends(get_authenticated_user)):
    return user


@app.post("/company/profile")
def create_company_profile(
    request: CompanyProfileRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")

    query_db(
        """
        INSERT INTO company_profiles
        (user_id, company_name, location, description, contact_information, website)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            company_name = VALUES(company_name),
            location = VALUES(location),
            description = VALUES(description),
            contact_information = VALUES(contact_information),
            website = VALUES(website)
        """,
        (
            user["id"],
            request.company_name.strip(),
            request.location.strip(),
            request.description,
            request.contact_information,
            request.website,
        ),
        commit=True,
    )

    return {"message": "Company profile created or updated"}


@app.get("/company/profile")
def get_company_profile(user=Depends(get_authenticated_user)):
    require_role(user, "company")

    profile = query_db(
        "SELECT * FROM company_profiles WHERE user_id = %s",
        (user["id"],),
        fetch="one",
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.put("/company/profile")
def update_company_profile(
    request: CompanyProfileRequest,
    user=Depends(get_authenticated_user),
):

    require_role(user, "company")

    query_db(
        """
        INSERT INTO company_profiles
        (user_id, company_name, location, description,
         contact_information, website)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        company_name = VALUES(company_name),
        location = VALUES(location),
        description = VALUES(description),
        contact_information = VALUES(contact_information),
        website = VALUES(website)
        """,
        (
            user["id"],
            request.company_name,
            request.location,
            request.description,
            request.contact_information,
            request.website,
        ),
        commit=True,
    )

    return {"message": "Company profile updated"}


@app.put("/student/profile")
def update_student_profile(
    request: StudentProfileRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "student")

    query_db(
        """
        INSERT INTO student_profiles
        (
            user_id,
            date_of_birth,
            city,
            state,
            country,
            career_objective,
            college,
            degree,
            major,
            graduation_year,
            cgpa,
            experience,
            phone
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            date_of_birth = VALUES(date_of_birth),
            city = VALUES(city),
            state = VALUES(state),
            country = VALUES(country),

            career_objective = VALUES(career_objective),
            college = VALUES(college),
            degree = VALUES(degree),
            major = VALUES(major),
            graduation_year = VALUES(graduation_year),
            cgpa = VALUES(cgpa),
            experience = VALUES(experience),
            phone = VALUES(phone)
        """,
        (
            user["id"],
            request.date_of_birth,
            request.city,
            request.state,
            request.country,
            request.career_objective,
            request.college,
            request.degree,
            request.major,
            request.graduation_year,
            request.cgpa,
            request.experience,
            request.phone,
        ),
        commit=True,
    )

    return {"message": "Student profile updated successfully"}

class JobUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    deadline: date
    location: str = Field(min_length=1, max_length=200)
    salary: Decimal | None = Field(default=None, ge=0)
    description: str = Field(min_length=1)
    category: str
    is_remote: bool = False


@app.post("/jobs", status_code=201, tags=["Jobs"])
def create_job(
    request: JobCreateRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")
    require_company_profile(user["id"])

    if request.category.strip().lower() not in JOB_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Category must be one of: {sorted(JOB_CATEGORIES)}",
        )

    job_id = query_db(
        """
        INSERT INTO jobs
        (company_user_id, title, posting_date, deadline, location, salary,
         description, category, is_remote)
        VALUES (%s, %s, CURRENT_DATE(), %s, %s, %s, %s, %s, %s)
        """,
        (
            user["id"],
            request.title.strip(),
            request.deadline,
            request.location.strip(),
            request.salary,
            request.description,
            request.category.strip().lower(),
            request.is_remote,
        ),
        commit=True,
    )

    return {"id": job_id, "message": "Job created"}
@app.get("/jobs", tags=["Jobs"])
def search_jobs(
    title: str | None = None,
    company: str | None = None,
    category: str | None = None,
    city: str | None = None,
    remote: bool | None = None,
    minimum_salary: Decimal | None = Query(default=None, ge=0),
    maximum_salary: Decimal | None = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    sql = """
        SELECT j.id, j.company_user_id, j.title, j.posting_date,
               j.deadline, j.location, j.salary, j.description,
               j.category, j.is_remote, j.created_at,
               c.company_name, c.website, c.location AS company_location
        FROM jobs j
        LEFT JOIN company_profiles c ON c.user_id = j.company_user_id
        WHERE j.deadline >= CURDATE()
    """
    params = []

    if title:
        sql += " AND j.title LIKE %s"
        params.append(f"%{title.strip()}%")

    if company:
        sql += " AND c.company_name LIKE %s"
        params.append(f"%{company.strip()}%")

    if category:
        sql += " AND LOWER(j.category) = %s"
        params.append(category.strip().lower())

    if city:
        sql += " AND j.location LIKE %s"
        params.append(f"%{city.strip()}%")

    if remote is not None:
        sql += " AND j.is_remote = %s"
        params.append(remote)

    if minimum_salary is not None:

        sql += " AND j.salary >= %s"
        params.append(minimum_salary)

    if maximum_salary is not None:
        sql += " AND j.salary <= %s"
        params.append(maximum_salary)

    sql += " ORDER BY j.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    return query_db(sql, tuple(params))


@app.get("/jobs/{job_id}", tags=["Jobs"])
def get_job_details(job_id: int):
    job = query_db(
        """
        SELECT j.id, j.company_user_id, j.title, j.posting_date,
               j.deadline, j.location, j.salary, j.description,
               j.category, j.is_remote, j.created_at,
               c.company_name, c.website, c.description AS company_description
        FROM jobs j
        LEFT JOIN company_profiles c ON c.user_id = j.company_user_id
        WHERE j.id = %s
        """,
        (job_id,),
        fetch="one",
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@app.put("/jobs/{job_id}", tags=["Jobs"])
def update_job(
    job_id: int,
    request: JobUpdateRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")
    owned_job(job_id, user["id"])

    if request.category.strip().lower() not in JOB_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid job category")

    query_db(
        """
        UPDATE jobs
        SET title = %s, deadline = %s, location = %s,
            salary = %s, description = %s, category = %s,
            is_remote = %s
        WHERE id = %s
        """,
        (
            request.title.strip(),
            request.deadline,
            request.location.strip(),
            request.salary,

            request.description,
            request.category.strip().lower(),
            request.is_remote,
            job_id,
        ),
        commit=True,
    )

    return {"message": "Job updated"}


@app.delete("/jobs/{job_id}", tags=["Jobs"])
def delete_job(
    job_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")
    owned_job(job_id, user["id"])

    query_db(
        "DELETE FROM jobs WHERE id = %s",
        (job_id,),
        commit=True,
    )

    return {"message": "Job deleted"}


@app.get("/company/jobs", tags=["Jobs"])
def company_jobs(user=Depends(get_authenticated_user)):
    require_role(user, "company")

    return query_db(
        """
        SELECT j.*,
               (SELECT COUNT(*) FROM applications a
                WHERE a.job_id = j.id) AS application_count
        FROM jobs j
        WHERE j.company_user_id = %s
        ORDER BY j.created_at DESC
        """,
        (user["id"],),
    )



@app.post("/events", status_code=201, tags=["Events"])
def create_event(
    request: EventCreateRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")
    require_company_profile(user["id"])

    event_id = query_db(
        """
        INSERT INTO events
        (company_user_id, name, description, event_date,
         event_time, location, eligibility)
        VALUES (%s, %s, %s, %s, %s, %s, %s)

        """,
        (
            user["id"],
            request.name.strip(),
            request.description,
            request.event_date,
            request.event_time,
            request.location.strip(),
            request.eligibility,
        ),
        commit=True,
    )

    return {"id": event_id, "message": "Event created"}


@app.get("/events", tags=["Events"])
def search_events(
    name: str | None = None,
    city: str | None = None,
    event_date: date | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    sql = """
        SELECT e.*, c.company_name
        FROM events e
        LEFT JOIN company_profiles c ON c.user_id = e.company_user_id
        WHERE e.event_date >= CURDATE()
    """
    params = []

    if name:
        sql += " AND e.name LIKE %s"
        params.append(f"%{name.strip()}%")

    if city:
        sql += " AND e.location LIKE %s"
        params.append(f"%{city.strip()}%")

    if event_date:
        sql += " AND e.event_date = %s"
        params.append(event_date)

    sql += " ORDER BY e.event_date, e.event_time LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    return query_db(sql, tuple(params))


@app.get("/events/{event_id}", tags=["Events"])
def get_event_details(event_id: int):
    event = query_db(
        """
        SELECT e.*, c.company_name, c.website
        FROM events e
        LEFT JOIN company_profiles c ON c.user_id = e.company_user_id
        WHERE e.id = %s
        """,
        (event_id,),

        fetch="one",
    )

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@app.put("/events/{event_id}", tags=["Events"])
def update_event(
    event_id: int,
    request: EventCreateRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")
    owned_event(event_id, user["id"])

    query_db(
        """
        UPDATE events
        SET name = %s, description = %s, event_date = %s,
            event_time = %s, location = %s, eligibility = %s
        WHERE id = %s
        """,
        (
            request.name.strip(),
            request.description,
            request.event_date,
            request.event_time,
            request.location.strip(),
            request.eligibility,
            event_id,
        ),
        commit=True,
    )

    return {"message": "Event updated"}


@app.delete("/events/{event_id}", tags=["Events"])
def delete_event(
    event_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")
    owned_event(event_id, user["id"])

    query_db(
        "DELETE FROM events WHERE id = %s",
        (event_id,),
        commit=True,
    )

    return {"message": "Event deleted"}


@app.post("/events/{event_id}/register", status_code=201, tags=["Events"])
def register_for_event(
    event_id: int,

    user=Depends(get_authenticated_user),
):
    require_role(user, "student")

    event = query_db(
        """
        SELECT id FROM events
        WHERE id = %s AND event_date >= CURDATE()
        """,
        (event_id,),
        fetch="one",
    )

    if not event:
        raise HTTPException(status_code=404, detail="Event not found or already passed")

    existing = query_db(
        """
        SELECT id FROM event_registrations
        WHERE event_id = %s AND student_user_id = %s
        """,
        (event_id, user["id"]),
        fetch="one",
    )

    if existing:
        raise HTTPException(status_code=409, detail="Already registered")

    registration_id = query_db(
        """
        INSERT INTO event_registrations (event_id, student_user_id)
        VALUES (%s, %s)
        """,
        (event_id, user["id"]),
        commit=True,
    )

    return {"id": registration_id, "message": "Registered for event"}


@app.delete("/events/{event_id}/register", tags=["Events"])
def unregister_from_event(
    event_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "student")

    registration = query_db(
        """
        SELECT id FROM event_registrations
        WHERE event_id = %s AND student_user_id = %s
        """,
        (event_id, user["id"]),
        fetch="one",
    )

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    query_db(

        """
        DELETE FROM event_registrations
        WHERE event_id = %s AND student_user_id = %s
        """,
        (event_id, user["id"]),
        commit=True,
    )

    return {"message": "Event registration cancelled"}


@app.get("/events/student/registrations", tags=["Events"])
def student_event_registrations(user=Depends(get_authenticated_user)):
    require_role(user, "student")

    return query_db(
        """
        SELECT e.*, er.registered_at, c.company_name
        FROM event_registrations er
        JOIN events e ON e.id = er.event_id
        LEFT JOIN company_profiles c ON c.user_id = e.company_user_id
        WHERE er.student_user_id = %s
        ORDER BY e.event_date, e.event_time
        """,
        (user["id"],),
    )


@app.get("/events/{event_id}/registrants", tags=["Events"])
def event_registrants(
    event_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "company")
    owned_event(event_id, user["id"])

    return query_db(
        """
        SELECT u.id AS student_id, u.name, u.email,
               sp.college, sp.major, sp.degree,
               er.registered_at
        FROM event_registrations er
        JOIN users u ON u.id = er.student_user_id
        LEFT JOIN student_profiles sp ON sp.user_id = u.id
        WHERE er.event_id = %s
        ORDER BY er.registered_at DESC
        """,
        (event_id,),
    )



@app.get("/student/preferences", tags=["Preferences"])
def get_student_preferences(user=Depends(get_authenticated_user)):
    require_role(user, "student")

    preferences = query_db(
        "SELECT * FROM student_preferences WHERE student_user_id = %s",
        (user["id"],),
        fetch="one",

    )

    if not preferences:
        return {
            "preferred_categories": [],
            "preferred_cities": [],
            "preferred_skills": [],
            "remote_only": False,
            "minimum_salary": None,
        }

    for field in (
        "preferred_categories",
        "preferred_cities",
        "preferred_skills",
    ):
        value = preferences.get(field)
        if isinstance(value, str):
            try:
                preferences[field] = json.loads(value)
            except (ValueError, TypeError):
                preferences[field] = []

    return preferences


@app.put("/student/preferences", tags=["Preferences"])
def update_student_preferences(
    request: PreferencesRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "student")

    query_db(
        """
        INSERT INTO student_preferences
        (student_user_id, preferred_categories, preferred_cities,
         preferred_skills, remote_only, minimum_salary)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            preferred_categories = VALUES(preferred_categories),
            preferred_cities = VALUES(preferred_cities),
            preferred_skills = VALUES(preferred_skills),
            remote_only = VALUES(remote_only),
            minimum_salary = VALUES(minimum_salary)
        """,
        (
            user["id"],
            json.dumps(request.preferred_categories or []),
            json.dumps(request.preferred_cities or []),
            json.dumps(request.preferred_skills or []),
            request.remote_only,
            request.minimum_salary,
        ),
        commit=True,
    )

    return {"message": "Preferences saved"}



@app.get("/search/students", tags=["Search"])
def search_students(
    name: str | None = None,
    college: str | None = None,
    major: str | None = None,
    city: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
):
    sql = """
        SELECT u.id, u.name, sp.city, sp.state, sp.college,
               sp.degree, sp.major, sp.graduation_year,
               sp.career_objective, sp.experience
        FROM users u
        JOIN student_profiles sp ON sp.user_id = u.id
        WHERE u.role = 'student'
    """
    params = []

    if name:
        sql += " AND u.name LIKE %s"
        params.append(f"%{name.strip()}%")

    if college:
        sql += " AND sp.college LIKE %s"
        params.append(f"%{college.strip()}%")

    if major:
        sql += " AND sp.major LIKE %s"
        params.append(f"%{major.strip()}%")

    if city:
        sql += " AND sp.city LIKE %s"
        params.append(f"%{city.strip()}%")

    sql += " ORDER BY u.name LIMIT %s"
    params.append(limit)

    return query_db(sql, tuple(params))


@app.get("/search/companies", tags=["Search"])
def search_companies(
    name: str | None = None,
    location: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
):
    sql = """
        SELECT cp.user_id, cp.company_name, cp.location,
               cp.description, cp.website
        FROM company_profiles cp
        JOIN users u ON u.id = cp.user_id
        WHERE u.role = 'company'
    """
    params = []

    if name:
        sql += " AND cp.company_name LIKE %s"
        params.append(f"%{name.strip()}%")

    if location:
        sql += " AND cp.location LIKE %s"
        params.append(f"%{location.strip()}%")

    sql += " ORDER BY cp.company_name LIMIT %s"
    params.append(limit)

    return query_db(sql, tuple(params))



class SaveItemRequest(BaseModel):
    item_type: str
    item_id: int


@app.post("/saved-items", status_code=201, tags=["Saved Items"])
def save_item(
    request: SaveItemRequest,
    user=Depends(get_authenticated_user),
):
    require_role(user, "student")

    item_type = request.item_type.strip().lower()

    if item_type not in {"job", "event"}:
        raise HTTPException(status_code=400, detail="item_type must be job or event")

    table = "jobs" if item_type == "job" else "events"

    item = query_db(
        f"SELECT id FROM {table} WHERE id = %s",
        (request.item_id,),
        fetch="one",
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = query_db(
        """
        SELECT id FROM saved_items
        WHERE student_user_id = %s AND item_type = %s AND item_id = %s
        """,
        (user["id"], item_type, request.item_id),
        fetch="one",
    )

    if existing:
        raise HTTPException(status_code=409, detail="Item already saved")

    saved_id = query_db(
        """
        INSERT INTO saved_items (student_user_id, item_type, item_id)
        VALUES (%s, %s, %s)
        """,
        (user["id"], item_type, request.item_id),
        commit=True,
    )

    return {"id": saved_id, "message": "Item saved"}


@app.get("/saved-items", tags=["Saved Items"])
def list_saved_items(user=Depends(get_authenticated_user)):
    require_role(user, "student")

    saved = query_db(
        """
        SELECT id, item_type, item_id, saved_at
        FROM saved_items
        WHERE student_user_id = %s
        ORDER BY saved_at DESC
        """,
        (user["id"],),
    )

    results = []

    for item in saved:
        if item["item_type"] == "job":
            details = query_db(
                """
                SELECT j.*, c.company_name
                FROM jobs j
                LEFT JOIN company_profiles c ON c.user_id = j.company_user_id
                WHERE j.id = %s
                """,
                (item["item_id"],),
                fetch="one",
            )
        else:
            details = query_db(
                """
                SELECT e.*, c.company_name
                FROM events e
                LEFT JOIN company_profiles c ON c.user_id = e.company_user_id
                WHERE e.id = %s
                """,
                (item["item_id"],),
                fetch="one",
            )

        results.append({**item, "details": details})

    return results


@app.delete("/saved-items/{saved_item_id}", tags=["Saved Items"])
def unsave_item(
    saved_item_id: int,
    user=Depends(get_authenticated_user),
):
    require_role(user, "student")

    saved = query_db(
        """
        SELECT id FROM saved_items
        WHERE id = %s AND student_user_id = %s
        """,

        (saved_item_id, user["id"]),
        fetch="one",
    )

    if not saved:
        raise HTTPException(status_code=404, detail="Saved item not found")

    query_db(
        "DELETE FROM saved_items WHERE id = %s",
        (saved_item_id,),
        commit=True,
    )

    return {"message": "Item removed from saved items"}



@app.get("/dashboard/student", tags=["Dashboard"])
def student_dashboard(user=Depends(get_authenticated_user)):
    require_role(user, "student")

    return {
        "applications": query_db(
            """
            SELECT status, COUNT(*) AS count
            FROM applications
            WHERE student_user_id = %s
            GROUP BY status
            """,
            (user["id"],),
        ),
        "upcoming_events": query_db(
            """
            SELECT e.id, e.name, e.event_date, e.event_time, e.location
            FROM event_registrations er
            JOIN events e ON e.id = er.event_id
            WHERE er.student_user_id = %s
              AND e.event_date >= CURDATE()
            ORDER BY e.event_date, e.event_time
            LIMIT 10
            """,
            (user["id"],),
        ),
        "saved_items_count": query_db(
            "SELECT COUNT(*) AS count FROM saved_items WHERE student_user_id = %s",
            (user["id"],),
            fetch="one",
        ),
    }


@app.get("/dashboard/company", tags=["Dashboard"])
def company_dashboard(user=Depends(get_authenticated_user)):
    require_role(user, "company")

    return {
        "jobs_count": query_db(
            "SELECT COUNT(*) AS count FROM jobs WHERE company_user_id = %s",
            (user["id"],),
            fetch="one",

        ),
        "events_count": query_db(
            "SELECT COUNT(*) AS count FROM events WHERE company_user_id = %s",
            (user["id"],),
            fetch="one",
        ),
        "applications": query_db(
            """
            SELECT a.status, COUNT(*) AS count
            FROM applications a
            JOIN jobs j ON j.id = a.job_id
            WHERE j.company_user_id = %s
            GROUP BY a.status
            """,
            (user["id"],),
        ),
    }