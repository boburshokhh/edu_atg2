# Research / Decisions

## Decision: Django + DRF as API platform
- **Rationale**: стандарт для Python backend, быстрое CRUD, хорошая расширяемость, админка из коробки.
- **Alternatives**: FastAPI (быстрее на старте, но больше ручной сборки для админки/permissions).

## Decision: PostgreSQL as source of truth for users + progress
- **Rationale**: уже есть целевая SQL-схема (`migrations/complete_database_schema.sql`), нужно хранить прогресс сотрудников в БД.
- **Alternatives**: Supabase/hosted auth — отклонено (фронт сейчас частично зависит от Supabase напрямую, но цель — свой backend).

## Decision: JWT access+refresh with revocation via DB sessions
- **Rationale**: в репо уже есть референс реализации и таблица `user_sessions`. Это позволяет logout/revoke refresh.
- **Alternatives**: pure stateless JWT refresh без хранения — не позволяет отзыв токена.

## Decision: MinIO integration via S3 API (boto3)
- **Rationale**: MinIO совместим с S3; boto3 позволяет presigned URL + чтение объектов с Range.
- **Alternatives**: прямой доступ к MinIO из браузера — отклонено (секреты в фронте, CORS/HTTPS проблемы).

## Decision: Streaming strategy
- **Primary**: выдача presigned download URL (MinIO сам поддерживает Range).
- **Secondary (recommended)**: proxy endpoint `GET /files/stream/{key}` с Range поддержкой для обхода CORS/mixed content и контроля доступа.

## Open Questions (NEEDS CLARIFICATION)
- Требуемые SLA/RPS и лимиты размера файлов.
- Нужно ли строго сохранить ответы 1-в-1 с существующим Node API (или допустимы новые `/api/v1` + алиасы).











