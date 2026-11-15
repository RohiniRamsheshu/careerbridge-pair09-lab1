"""Student-domain operations behind the existing API contract."""


def get_profile(query_db, user_id):
    return query_db(
        """
        SELECT u.id, u.name, u.email, sp.date_of_birth, sp.city, sp.state,
               sp.country, sp.career_objective, sp.college, sp.degree,
               sp.major, sp.graduation_year, sp.cgpa, sp.experience, sp.phone,
               sp.profile_picture
        FROM users u
        JOIN student_profiles sp ON sp.user_id = u.id
        WHERE u.id = %s
        """,
        (user_id,),
        fetch="one",
    )


def update_profile(query_db, user_id, request):
    if request.name is not None:
        query_db(
            "UPDATE users SET name = %s WHERE id = %s AND role = 'student'",
            (request.name.strip(), user_id),
            commit=True,
        )

    query_db(
        """
        INSERT INTO student_profiles
        (
            user_id, date_of_birth, city, state, country, career_objective,
            college, degree, major, graduation_year, cgpa, experience, phone
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
            user_id,
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
