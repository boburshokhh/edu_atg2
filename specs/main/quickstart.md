# Quickstart (Docker)

## Prerequisites
- Docker Desktop

## Run

1) Создайте `.env` рядом с `docker-compose.yml` (см. `.env.example` после генерации backend кода)
2) Запуск:

```bash
docker compose up --build
```

## API
- `GET /health`
- Auth: `POST /auth/login`

## Notes
- Postgres хранит пользователей/прогресс/контент-метаданные.
- MinIO хранит файлы материалов; доступ — через presigned URL или `/files/stream/{key}`.











