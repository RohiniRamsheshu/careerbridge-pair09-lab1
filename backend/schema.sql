SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `users` (
`id` bigint unsigned NOT NULL AUTO_INCREMENT,
`name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
`email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
`password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
`role` enum('student','company') COLLATE utf8mb4_unicode_ci NOT NULL,
`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`id`),
UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `company_profiles` (
`user_id` bigint unsigned NOT NULL,
`company_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
`location` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
`description` text COLLATE utf8mb4_unicode_ci,
`contact_information` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`profile_picture` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`website` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
PRIMARY KEY (`user_id`),
CONSTRAINT `company_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `student_profiles` (
`user_id` bigint unsigned NOT NULL,
`date_of_birth` date DEFAULT NULL,
`city` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`state` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`country` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`career_objective` text COLLATE utf8mb4_unicode_ci,
`college` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
`degree` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`major` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`graduation_year` smallint DEFAULT NULL,
`cgpa` decimal(4,2) DEFAULT NULL,
`experience` text COLLATE utf8mb4_unicode_ci,
`phone` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`profile_picture` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
PRIMARY KEY (`user_id`),
CONSTRAINT `student_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jobs` (
`id` bigint unsigned NOT NULL AUTO_INCREMENT,
`company_user_id` bigint unsigned NOT NULL,
`title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
`posting_date` date NOT NULL,
`deadline` date NOT NULL,
`location` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
`salary` decimal(12,2) DEFAULT NULL,
`description` text COLLATE utf8mb4_unicode_ci NOT NULL,
`category` enum('full time','part time','on campus','internship') COLLATE utf8mb4_unicode_ci NOT NULL,
`is_remote` tinyint(1) NOT NULL DEFAULT '0',
`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`id`),
KEY `company_user_id` (`company_user_id`),
KEY `idx_jobs_title` (`title`),
KEY `idx_jobs_location` (`location`),
KEY `idx_jobs_category` (`category`),
KEY `idx_jobs_deadline` (`deadline`),
CONSTRAINT `jobs_ibfk_1` FOREIGN KEY (`company_user_id`) REFERENCES `company_profiles` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `events` (
`id` bigint unsigned NOT NULL AUTO_INCREMENT,
`company_user_id` bigint unsigned NOT NULL,
`name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
`description` text COLLATE utf8mb4_unicode_ci NOT NULL,
`event_date` date NOT NULL,
`event_time` time NOT NULL,
`location` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
`eligibility` text COLLATE utf8mb4_unicode_ci,
`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`id`),
KEY `company_user_id` (`company_user_id`),
KEY `idx_events_date` (`event_date`),
KEY `idx_events_name` (`name`),
CONSTRAINT `events_ibfk_1` FOREIGN KEY (`company_user_id`) REFERENCES `company_profiles` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `applications` (
`id` bigint unsigned NOT NULL AUTO_INCREMENT,
`job_id` bigint unsigned NOT NULL,
`student_user_id` bigint unsigned NOT NULL,
`resume_path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
`status` enum('Pending','Reviewed','Declined') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Pending',
`applied_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`id`),
UNIQUE KEY `uq_application_student_job` (`job_id`,`student_user_id`),
KEY `student_user_id` (`student_user_id`),
CONSTRAINT `applications_ibfk_1` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE CASCADE,
CONSTRAINT `applications_ibfk_2` FOREIGN KEY (`student_user_id`) REFERENCES `student_profiles` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `event_registrations` (
`id` bigint unsigned NOT NULL AUTO_INCREMENT,
`event_id` bigint unsigned NOT NULL,
`student_user_id` bigint unsigned NOT NULL,
`registered_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`id`),
UNIQUE KEY `uq_event_registration` (`event_id`,`student_user_id`),
KEY `student_user_id` (`student_user_id`),
CONSTRAINT `event_registrations_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE,
CONSTRAINT `event_registrations_ibfk_2` FOREIGN KEY (`student_user_id`) REFERENCES `student_profiles` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `saved_items` (
`id` bigint unsigned NOT NULL AUTO_INCREMENT,
`student_user_id` bigint unsigned NOT NULL,
`item_type` enum('job','event') COLLATE utf8mb4_unicode_ci NOT NULL,
`item_id` bigint unsigned NOT NULL,
`saved_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`id`),
UNIQUE KEY `uq_saved_item` (`student_user_id`,`item_type`,`item_id`),
CONSTRAINT `saved_items_ibfk_1` FOREIGN KEY (`student_user_id`) REFERENCES `student_profiles` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `student_preferences` (
`student_user_id` bigint unsigned NOT NULL,
`preferred_categories` json DEFAULT NULL,
`preferred_cities` json DEFAULT NULL,
`preferred_skills` json DEFAULT NULL,
`remote_only` tinyint(1) NOT NULL DEFAULT '0',
`minimum_salary` decimal(12,2) DEFAULT NULL,
`updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (`student_user_id`),
CONSTRAINT `student_preferences_ibfk_1` FOREIGN KEY (`student_user_id`) REFERENCES `student_profiles` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `student_skills` (
`id` bigint unsigned NOT NULL AUTO_INCREMENT,
`student_user_id` bigint unsigned NOT NULL,
`skill` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
PRIMARY KEY (`id`),
UNIQUE KEY `uq_student_skill` (`student_user_id`,`skill`),
CONSTRAINT `student_skills_ibfk_1` FOREIGN KEY (`student_user_id`) REFERENCES `student_profiles` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS=1;
