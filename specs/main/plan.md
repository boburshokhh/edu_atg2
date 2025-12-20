# Implementation Plan: ATG Education Backend (Django/DRF)

**Branch**: `main` | **Date**: 2025-12-15 | **Spec**: `specs/main/spec.md`
**Input**: Feature specification from `specs/main/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Сгенерировать backend на Django/DRF, совместимый с существующим фронтендом и текущими путями API, с PostgreSQL как источником истины для пользователей/прогресса и MinIO для хранения/стриминга материалов (PDF/видео/документы). Авторизация — JWT access+refresh с отзывом refresh через `user_sessions`. Для стриминга — presigned URL (и опциональный proxy endpoint с Range).

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12  
**Primary Dependencies**: Django, Django REST Framework, PyJWT (или SimpleJWT), boto3 (S3/MinIO), django-redis, django-cors-headers  
**Storage**: PostgreSQL (users/progress/domain data), MinIO (object storage), Redis (cache)  
**Testing**: pytest + pytest-django (NEEDS CLARIFICATION: требуемый минимум тестов в этом репо)  
**Target Platform**: Linux (Docker containers)  
**Project Type**: Web application (API backend + existing frontend)  
**Performance Goals**: корректная работа Range streaming; базовая производительность для обучения (NEEDS CLARIFICATION: target RPS/SLA)  
**Constraints**: минимальная ручная конфигурация, только env vars; совместимость API путей/ответов с фронтом  
**Scale/Scope**: монолит с разделением по apps, готовый к будущему выделению сервисов

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Docker-first, конфижим через env vars
- ✅ No secrets in repo (все значения в `.env.example`, реальные секреты — только env)
- ✅ JWT access+refresh + revocation (через `user_sessions` или blacklist)
- ✅ Streaming support (Range, 206 responses) — обязательный функционал

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend_django/
├── manage.py
├── pyproject.toml (или requirements.txt)
├── atg_backend/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/
│   ├── stations/
│   ├── learning/
│   ├── progress/
│   └── files/
└── docker/
    ├── Dockerfile
    └── entrypoint.sh

docker-compose.yml
.env.example
```

**Structure Decision**: Выбран монолитный Django backend в `backend_django/` с доменными apps, плюс root-level `docker-compose.yml` для Postgres/Redis/MinIO/API.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
