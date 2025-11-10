# MinIO - Быстрый старт

## Что было настроено

### 1. Сервис MinIO
- Создан файл `src/services/minioService.js`
- Настроен endpoint: `http://45.138.159.79:9001`
- Bucket: `atg-uploads`

### 2. Интеграция в админ-панель
- Добавлена вкладка "Файлы → в админ-панель"
- Реализована загрузка файлов (drag & drop)
- Реализован просмотр и скачивание файлов
- Реализовано удаление файлов

## Что нужно сделать

### 1. Создать таблицу в Supabase

Выполните SQL из `docs/MINIO_SETUP.md` в SQL Editor Supabase:

```sql
CREATE TABLE IF NOT EXISTS files (
  id BIGSERIAL PRIMARY KEY,
  object_name TEXT NOT NULL,
  file_name TEXT NOT NULL,
  original_name TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT,
  file_url TEXT NOT NULL,
  uploaded_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. Настроить MinIO

1. Откройте MinIO Console: http://45.138.159.79:9001
2. Войдите с учетными данными
3. Создайте bucket `atg-uploads`
4. Настройте CORS (Settings → CORS)

### 3. Проверить работу

1. Откройте админ-панель: http://localhost:5173/admin
2. Перейдите на вкладку "Файлы"
3. Загрузите тестовый файл
4. Проверьте отображение в списке

## Использование

### Загрузка файлов
- Drag & Drop: перетащите файлы в область загрузки
- Или нажмите для выбора файлов
- Нажмите "Загрузить файлы"

### Управление файлами
- **Просмотр**: откройте файл в новой вкладке
- **Скачать**: скачайте файл на компьютер
- **Удалить**: удалите файл из системы

## Важно!

Для полноценной работы требуется:
- ✅ MinIO доступен по адресу `http://45.138.159.79:9001`
- ✅ Bucket `atg-uploads` создан
- ✅ CORS настроен в MinIO
- ✅ Таблица `files` создана в Supabase

## Troubleshooting

### Ошибка CORS при загрузке
**Причина**: CORS не настроен в MinIO  
**Решение**: См. настройку CORS в MinIO Console

### Ошибка при сохранении в БД
**Причина**: Таблица `files` не создана  
**Решение**: Выполните SQL из `docs/MINIO_SETUP.md`

### Файлы не отображаются
**Причина**: Ошибка подключения к MinIO  
**Решение**: Проверьте доступность MinIO

## Документация

Полная документация: `docs/MINIO_SETUP.md`

