# ATG Education Backend Constitution

## Core Principles

### Docker-First & Env-Only Config
- Backend должен запускаться в Docker без ручных действий, кроме задания env vars.
- Секреты (JWT secrets, DB creds, MinIO keys) **никогда** не хардкодим в репо.

### Security Baseline (Non-negotiable)
- JWT access + refresh, refresh токены должны быть отзывными (revocable).
- Пароли храним только хешированные (bcrypt/compatible hasher).
- CORS только через конфиг, по умолчанию — безопасно (локальный dev и явно заданные origins).
- Защита заголовками (security headers), запрет debug в production.

### API Compatibility & Versioning
- Сохраняем совместимость с фронтом: пути и формы ответов не ломаем без миграционного периода.
- Новые API размещаем под `/api/v1` только если это не ломает текущий фронт; иначе — алиасы.

### Streaming is a First-Class Feature
- Для PDF/video обязана работать поддержка HTTP Range requests (206 + Content-Range + Accept-Ranges).
- Presigned URLs должны быть корректны и не добавлять конфликтующие заголовки (например, избегать дублирования `Content-Disposition`).

### Maintainable Monolith (ready for split)
- Внутри Django проект делим по доменам (apps): accounts, stations, learning, progress, files.
- Внутренние сервисы (MinIO, tokens) — изолированы и тестируемы.

## Quality Gates

- **No secrets in code**: запрет на ключи/пароли в репо.
- **Docs shipped**: OpenAPI контракт + quickstart.
- **Run in compose**: `docker compose up` поднимает API + Postgres + Redis + MinIO.

## Governance

Если для совместимости требуется отклонение от принципов, оно фиксируется в `specs/main/plan.md` (Complexity Tracking) с обоснованием и планом исправления.

**Version**: 1.0.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15
