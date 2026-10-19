SET FOREIGN_KEY_CHECKS=0;

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`) VALUES (1, 'Test Student', 'teststudent@example.com', '$2b$12$ATOo3h7YOxQGMhaCRDni1ucEpgd.Vq5XdCiXzLfuI4f1dAVY39.lO', 'student', '2026-10-18T00:40:52');

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`) VALUES (3, 'Test Company', 'testcompany@example.com', '$2b$12$9bUuCwnFW.J15uViQDOK8.1aLBl7OAPFOfyAuPuZ9mPlqqp5EOlke', 'company', '2026-10-18T03:33:15');

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`) VALUES (4, 'Test Company 2', 'testcompany2@example.com', '$2b$12$1L95O7yDo1qgnWTjkHHfM.zfqY5FDzjzBaE2Ia57p2urjOIQ/PCwK', 'company', '2026-10-18T11:28:25');

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`) VALUES (5, 'Backend Test Student', 'backendstudent01@example.com', '$2b$12$9948gRU6G1o217bPfMX1tuuONKxjHhuteQRFAJRE8HgVdu8Q0j8au', 'student', '2026-10-18T15:30:45');

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`) VALUES (7, 'Backend Test Student', '123@gmail.com', '$2b$12$30VGtTSEKO4GDvI7LGyZiO1KZN6igQcg7yCzldMFwVI9RC0ro/EgK', 'student', '2026-10-18T15:45:27');

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`) VALUES (8, 'Backend Test Recruiter', 'backendcompany01@example.com', '$2b$12$O081KiaXM9k8xkqXodiriOeZXIJ6kl.zAtpX0o9s9omY.apt4XeeC', 'company', '2026-10-18T15:47:13');

INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `role`, `created_at`) VALUES (9, 'Backend Test Recruiter', 'backendcompany02@example.com', '$2b$12$D.BuS7X84ejM06oH/Sd/ReS2T.T6X0SN0EnWrrRHr5wz0WhhUukiS', 'company', '2026-10-18T17:15:01');

INSERT INTO `company_profiles` (`user_id`, `company_name`, `location`, `description`, `contact_information`, `profile_picture`, `website`) VALUES (3, 'Test Company', 'San Jose', 'Test company for Handshake Lab 1', NULL, NULL, NULL);

INSERT INTO `company_profiles` (`user_id`, `company_name`, `location`, `description`, `contact_information`, `profile_picture`, `website`) VALUES (8, 'Test Tech Inc', 'San Jose, CA', NULL, NULL, NULL, NULL);

INSERT INTO `company_profiles` (`user_id`, `company_name`, `location`, `description`, `contact_information`, `profile_picture`, `website`) VALUES (9, 'Test Tech Inc', 'San Jose, CA', 'Technology company focused on software development, backend engineering, and building innovative applications.', 'hr@testtech.com', NULL, 'https://example.com');

INSERT INTO `student_profiles` (`user_id`, `date_of_birth`, `city`, `state`, `country`, `career_objective`, `college`, `degree`, `major`, `graduation_year`, `cgpa`, `experience`, `phone`, `profile_picture`) VALUES (1, NULL, NULL, NULL, NULL, NULL, 'San Jose State University', NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO `student_profiles` (`user_id`, `date_of_birth`, `city`, `state`, `country`, `career_objective`, `college`, `degree`, `major`, `graduation_year`, `cgpa`, `experience`, `phone`, `profile_picture`) VALUES (7, NULL, NULL, NULL, NULL, NULL, 'San Jose State University', NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO `jobs` (`id`, `company_user_id`, `title`, `posting_date`, `deadline`, `location`, `salary`, `description`, `category`, `is_remote`, `created_at`) VALUES (1, 3, 'Data Analyst Intern', '2026-10-18', '2026-12-31', 'San Jose', 25.00, 'Analyze datasets and create reports.', 'internship', 0, '2026-10-18T03:41:39');

INSERT INTO `events` (`id`, `company_user_id`, `name`, `description`, `event_date`, `event_time`, `location`, `eligibility`, `created_at`) VALUES (1, 9, 'Handshake Tech Networking Event - Updated', 'Updated networking event for students interested in software engineering, backend development, and technology careers.', '2026-10-30', '18:30:00', 'San Jose, CA', 'SJSU students enrolled in technology-related programs', '2026-10-18T17:31:59');

INSERT INTO `applications` (`id`, `job_id`, `student_user_id`, `resume_path`, `status`, `applied_at`) VALUES (3, 1, 1, 'backend/uploads/resumes/1_a839cd2fd0444c52b260d5c504ab1e9b.pdf', 'Pending', '2026-10-18T04:43:25');

SET FOREIGN_KEY_CHECKS=1;
