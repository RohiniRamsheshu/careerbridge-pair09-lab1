import random
import bcrypt
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from backend.app.database import get_connection

SEED = 9
random_state = SEED
rng = random.Random(random_state)

CITY_SET = ["San Jose", "Mountain View", "Palo Alto"]
PASSWORD = "SeedPass09!"

def fetch_count(cursor, table):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]

def main():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Create only the missing students.
        students_needed = max(0, 200 - fetch_count(cursor, "student_profiles"))
        companies_needed = max(0, 50 - fetch_count(cursor, "company_profiles"))

        password_hash = bcrypt.hashpw(
            PASSWORD.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        for i in range(1, students_needed + 1):
            email = f"pair09.student{i:04d}@example.com"
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()

            if row:
                user_id = row[0]
            else:
                cursor.execute(
                    """INSERT INTO users (name, email, password_hash, role)
                       VALUES (%s, %s, %s, %s)""",
                    (f"Seed Student {i:04d}", email, password_hash, "student")
                )
                user_id = cursor.lastrowid

            cursor.execute(
                "SELECT user_id FROM student_profiles WHERE user_id = %s",
                (user_id,)
            )
            if not cursor.fetchone():
                city = rng.choice(CITY_SET)
                cursor.execute(
                    """INSERT INTO student_profiles
                       (user_id, city, state, country, college, degree, major,
                        graduation_year, career_objective)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        user_id, city, "CA", "USA", "SJSU",
                        "Bachelor's", "Computer Science", 2027,
                        "Seeking an opportunity to build practical skills."
                    )
                )

        # Create only the missing companies.
        for i in range(1, companies_needed + 1):
            email = f"pair09.company{i:04d}@example.com"
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()

            if row:
                user_id = row[0]
            else:
                cursor.execute(
                    """INSERT INTO users (name, email, password_hash, role)
                       VALUES (%s, %s, %s, %s)""",
                    (f"Seed Company {i:04d}", email, password_hash, "company")
                )
                user_id = cursor.lastrowid

            cursor.execute(
                "SELECT user_id FROM company_profiles WHERE user_id = %s",
                (user_id,)
            )
            if not cursor.fetchone():
                city = rng.choice(CITY_SET)
                cursor.execute(
                    """INSERT INTO company_profiles
                       (user_id, company_name, location, description,
                        contact_information, website)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        user_id, f"Seed Company {i:04d}", city,
                        "Company profile created for Lab 1 seed data.",
                        f"pair09.company{i:04d}@example.com",
                        "https://example.com"
                    )
                )

        conn.commit()

        # Fetch valid student and company IDs from profiles.
        cursor.execute("SELECT user_id FROM student_profiles")
        student_ids = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT user_id FROM company_profiles")
        company_ids = [r[0] for r in cursor.fetchall()]

        if not student_ids or not company_ids:
            raise RuntimeError("Need student and company profiles before seeding jobs.")

        # Add jobs until the total reaches 300.
        jobs_needed = max(0, 300 - fetch_count(cursor, "jobs"))
        categories = ["full time", "part time", "on campus", "internship"]

        for i in range(jobs_needed):
            company_id = rng.choice(company_ids)
            city = rng.choice(CITY_SET)
            deadline = date.today() + timedelta(days=rng.randint(30, 365))

            cursor.execute(
                """INSERT INTO jobs
                   (company_user_id, title, posting_date, deadline, location,
                    salary, description, category, is_remote)
                   VALUES (%s, %s, CURRENT_DATE(), %s, %s, %s, %s, %s, %s)""",
                (
                    company_id,
                    f"Seed Job {i + 1:04d}",
                    deadline,
                    city,
                    Decimal(rng.randrange(40000, 150001)),
                    "Seed posting for Lab 1 testing.",
                    rng.choice(categories),
                    rng.choice([True, False])
                )
            )

        conn.commit()

        # Add events until the total reaches 100.
        events_needed = max(0, 100 - fetch_count(cursor, "events"))

        for i in range(events_needed):
            company_id = rng.choice(company_ids)
            city = rng.choice(CITY_SET)
            event_date = date.today() + timedelta(days=rng.randint(7, 180))
            event_time = time(rng.randint(9, 17), 0)

            cursor.execute(
                """INSERT INTO events
                   (company_user_id, name, description, event_date,
                    event_time, location, eligibility)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    company_id,
                    f"Seed Career Event {i + 1:04d}",
                    "Seed event for Lab 1 testing.",
                    event_date,
                    event_time,
                    city,
                    "Students"
                )
            )

        conn.commit()

        # Add applications with unique job/student pairs.
        applications_needed = max(
            0, 1500 - fetch_count(cursor, "applications")
        )

        cursor.execute("SELECT id FROM jobs")
        job_ids = [r[0] for r in cursor.fetchall()]

        if not job_ids or not student_ids:
            raise RuntimeError("Need jobs and students before seeding applications.")

        cursor.execute("SELECT job_id, student_user_id FROM applications")
        existing_pairs = set(cursor.fetchall())

        possible_pairs = [
            (job_id, student_id)
            for job_id in job_ids
            for student_id in student_ids
            if (job_id, student_id) not in existing_pairs
        ]
        rng.shuffle(possible_pairs)

        if len(possible_pairs) < applications_needed:
            raise RuntimeError(
                f"Not enough unique job/student pairs: "
                f"{len(possible_pairs)} available, "
                f"{applications_needed} needed."
            )

        for job_id, student_id in possible_pairs[:applications_needed]:
            cursor.execute(
                """INSERT INTO applications
                   (job_id, student_user_id, resume_path, status)
                   VALUES (%s, %s, %s, %s)""",
                (
                    job_id,
                    student_id,
                    f"seeded_resumes/student_{student_id}.pdf",
                    rng.choice(["Pending", "Reviewed", "Declined"])
                )
            )

        conn.commit()

        print("Seeding complete. Current totals:")
        for table in [
            "student_profiles", "company_profiles", "jobs",
            "applications", "events"
        ]:
            print(f"{table}: {fetch_count(cursor, table)}")

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
