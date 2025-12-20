# ATG Education Backend (Django/DRF) — Feature Spec

## Goal

Сгенерировать backend на **Python/Django** (PostgreSQL + Redis + MinIO), совместимый с текущим фронтендом (Vue) и существующими маршрутами, которые уже реализованы/задокументированы в репозитории.

Backend должен:
- хранить **все данные пользователей и прогресса** в PostgreSQL
- поддерживать **стриминг видео и документов** (HTTP Range requests)
- выдавать **presigned URLs** для MinIO (скачивание/загрузка) и/или **proxy streaming** через API
- обеспечивать **аутентификацию и авторизацию** через JWT (access+refresh), с хранением сессий в БД
- быть **Docker-ready**: запуск одной командой с PostgreSQL/Redis/MinIO через `docker-compose.yml`, конфигурация только через env vars

## Non-Goals (for initial iteration)

- Перенос/рефактор фронтенда (в этом таске генерируем только backend-код)
- Полный конструктор тестов/вопросов (если потребуется — отдельным этапом)

## Compatibility Requirements (from repo)

### Existing API routes (Node backend reference)

Нужно поддержать совместимый REST контракт (как минимум):
- `POST /auth/login` → `{ token, refreshToken, user, expiresIn }`
- `POST /auth/refresh` → `{ token, expiresIn }`
- `POST /auth/logout`
- `GET /auth/me`

Профиль:
- `GET /users/me`
- `PUT /users/me`
- `GET /users/me/stats`

Станции:
- `GET /stations`
- `GET /stations/{id}`
- `GET /stations/{id}/equipment`
- `GET /stations/{id}/specs`
- `GET /stations/{id}/safety`

Курсы:
- `GET /courses/stations/{stationId}` (список `courses` по станции)
- `GET /courses/{courseId}` (курс + `course_programs` по `station_id`)
- `GET /courses/{courseId}/programs`
- `POST /courses/{courseId}/enroll`
- `GET /courses/me/enrollments`

### File/Streaming requirements (frontend reference)

Фронтенд ожидает:
- возможность получить **URL** на файл (PDF/видео/документ) с поддержкой Range requests
- для PDF используется **PDF.js** с `disableRange=false`, значит сервер/MinIO должны отдавать `206 Partial Content` на Range запросы

Backend должен предоставить:
- `GET /files/presign` (presigned download URL)
- `POST /files/presign-upload` (presigned upload URL для админки/инструкторов)
- `GET /files/folder-contents` (list folders+files по prefix/delimiter)
- `GET /files/stream/{key}` (proxy streaming с Range поддержкой; опционально, но рекомендуется для обхода CORS/HTTPS проблем)

## Data Model

База данных должна соответствовать существующей схеме `migrations/complete_database_schema.sql`:
- `users`, `user_profiles`, `user_sessions`
- `stations` + дочерние таблицы
- `courses`, `user_courses`, `certificates`, `user_stats`
- `course_programs`, `lessons`, `topics`, `topic_files` и др.

Дополнительно для прогресса сотрудников:
- таблица прогресса по темам (минимально): `user_topic_progress` (user, topic, completed, timestamps)
- таблица результатов тестов (минимально): `user_test_results` (user, lesson_test/final_test, score, passed, timestamps)

## Security

- JWT access/refresh, refresh токены должны быть **revocable** (через таблицу `user_sessions` или blacklist)
- CORS configurable через env
- rate limiting/headers (минимальный baseline)
- secrets только через env

## Deliverables

1) Docs/specs: `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`
2) Django project code (models/serializers/views/urls) + Docker setup
3) MinIO integration: presign + пример proxy streaming с Range + пример генерации presigned URL










