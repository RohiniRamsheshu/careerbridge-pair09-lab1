"""Application-domain queries behind the existing `/applications` contract."""


def list_for_student(run_query, student_id):
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
        (student_id,),
    )


def owned_applicants(run_query, job_id, company_id):
    job = run_query(
        "SELECT id FROM jobs WHERE id = %s AND company_user_id = %s",
        (job_id, company_id),
        fetch="one",
    )
    if not job:
        return None, None
    rows = run_query(
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
    return job, rows


def applicant_profile(run_query, job_id, application_id, company_id):
    return run_query(
        """
        SELECT u.id AS student_id, u.name, u.email,
               sp.date_of_birth, sp.city, sp.state, sp.country,
               sp.career_objective, sp.college, sp.degree, sp.major,
               sp.graduation_year, sp.cgpa, sp.experience, sp.phone,
               CASE WHEN sp.profile_picture IS NOT NULL THEN 1 ELSE 0 END
                   AS profile_picture_available,
               CASE WHEN a.resume_path IS NOT NULL THEN 1 ELSE 0 END
                   AS resume_available
        FROM applications a
        JOIN jobs j ON j.id = a.job_id AND j.company_user_id = %s
        JOIN users u ON u.id = a.student_user_id
        LEFT JOIN student_profiles sp ON sp.user_id = u.id
        WHERE a.id = %s AND a.job_id = %s
        """,
        (company_id, application_id, job_id),
        fetch="one",
    )


def applicant_resume(run_query, job_id, application_id, company_id):
    return run_query(
        """
        SELECT a.resume_path
        FROM applications a
        JOIN jobs j ON j.id = a.job_id AND j.company_user_id = %s
        WHERE a.id = %s AND a.job_id = %s
        """,
        (company_id, application_id, job_id),
        fetch="one",
    )


def update_status(run_query, job_id, application_id, company_id, status):
    application = run_query(
        """
        SELECT a.id
        FROM applications a
        JOIN jobs j ON j.id = a.job_id
        WHERE a.id = %s AND a.job_id = %s AND j.company_user_id = %s
        """,
        (application_id, job_id, company_id),
        fetch="one",
    )
    if not application:
        return False
    run_query(
        "UPDATE applications SET status = %s WHERE id = %s",
        (status, application_id),
        commit=True,
    )
    return application_id


def update_status_with_outbox(connection_factory, job_id, application_id, company_id,
                              status, enqueue_event, make_event):
    connection = connection_factory()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT a.id FROM applications a
            JOIN jobs j ON j.id = a.job_id
            WHERE a.id = %s AND a.job_id = %s AND j.company_user_id = %s
            """,
            (application_id, job_id, company_id),
        )
        application = cursor.fetchone()
        if not application:
            connection.rollback()
            return False

        cursor.execute(
            "UPDATE applications SET status = %s WHERE id = %s",
            (status, application_id),
        )
        payload = {"job_id": job_id, "status": status}
        enqueue_event(cursor, make_event("application.updated", application_id, "application", payload))
        enqueue_event(cursor, make_event("application.status_changed", application_id, "application", payload))
        connection.commit()
        return application_id
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
