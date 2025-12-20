# Data Model (PostgreSQL)

Основа — существующая схема `migrations/complete_database_schema.sql`. Ниже — доменные сущности и связи, которые будет отражать Django ORM (с сохранением `db_table`/полей).

## Accounts

- **users**
  - `id` UUID PK
  - `username` unique
  - `password_hash` (Django field `password` с `db_column='password_hash'`)
  - `full_name`, `email`
  - `role`: `admin|user|instructor`
  - `is_active`
  - `created_at`, `updated_at`

- **user_profiles** (1:1 к users, PK = user_id)
  - `avatar_url`, `company`, `position`, `phone`, `bio`, `language`
  - notification flags
  - `created_at`, `updated_at`

- **user_sessions**
  - `id` UUID PK
  - `user_id` FK users
  - `session_token` (refresh token JWT string)
  - `expires_at`, `created_at`, `last_activity`, `ip_address`, `user_agent`

## Stations

- **stations** (PK int serial)
- **station_gas_supply_sources** (FK station)
- **station_equipment** (FK station)
- **station_specifications** (FK station)
- **station_safety_systems** (FK station)
- **station_safety_system_features** (FK safety_system)

## Learning content

- **course_programs** (FK station)
- **course_program_learning_outcomes** (FK course_program)
- **course_program_requirements** (FK course_program)
- **course_program_target_audience** (FK course_program)

- **lessons** (FK course_program)
- **topics** (FK lesson)
- **topic_files** (FK topic)
  - `file_type`: `main_pdf|additional_video|additional_document`
  - `minio_object_name` (ключ объекта в MinIO)
  - `file_url` (может кешировать последний presigned URL, но primary source — `minio_object_name`)

- **lesson_materials** (FK lesson)
- **lesson_tests** (FK lesson)
- **final_tests** (FK course_program)

## Courses & Progress

- **courses** (UUID PK, FK station nullable) — “карточка курса” (быстрый список для станции)
- **user_courses** (user<->course, unique(user_id, course_id)) — прогресс курса
- **certificates** (FK user, FK course)
- **user_stats** (PK=user_id) — агрегаты

## Additional progress (new tables)

Чтобы прогресс тем/тестов не был только в localStorage, добавляем:

- **user_topic_progress**
  - `id` UUID PK
  - `user_id` FK users
  - `topic_id` FK topics
  - `completed` boolean
  - `completed_at`, `last_activity`, `created_at`, `updated_at`
  - unique(user_id, topic_id)

- **user_test_results**
  - `id` UUID PK
  - `user_id` FK users
  - `lesson_test_id` FK lesson_tests NULL
  - `final_test_id` FK final_tests NULL
  - `score_percent` int
  - `passed` boolean
  - timestamps
  - constraint: ровно одно из (`lesson_test_id`, `final_test_id`) не NULL










