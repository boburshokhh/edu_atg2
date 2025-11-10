# Настройка MinIO для админ-панели

## Обзор

В админ-панели настроена интеграция с MinIO для загрузки и управления файлами.

## Конфигурация

### Сервис MinIO
- **Endpoint**: `http://45.138.159.79:9001`
- **Bucket**: `atg-uploads`
- **Файл сервиса**: `src/services/minioService.js`

## Создание таблицы в Supabase

Выполните следующий SQL в Supabase для создания таблицы `files`:

```sql
-- Создание таблицы для хранения информации о файлах
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

-- Создание индекса для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_files_object_name ON files(object_name);
CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON files(uploaded_at DESC);

-- Включение Row Level Security (RLS)
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Политика доступа для всех пользователей (для чтения)
CREATE POLICY "Allow public read access" ON files
  FOR SELECT
  USING (true);

-- Политика доступа для администраторов (для записи и удаления)
CREATE POLICY "Allow admin write access" ON files
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'admin'
    )
  );

-- Комментарии к таблице
COMMENT ON TABLE files IS 'Информация о файлах, загруженных в MinIO';
COMMENT ON COLUMN files.object_name IS 'Имя объекта в MinIO';
COMMENT ON COLUMN files.file_name IS 'Сгенерированное имя файла';
COMMENT ON COLUMN files.original_name IS 'Оригинальное имя файла';
COMMENT ON COLUMN files.file_size IS 'Размер файла в байтах';
COMMENT ON COLUMN files.file_type IS 'MIME тип файла';
COMMENT ON COLUMN files.file_url IS 'URL для доступа к файлу';
```

## Настройка MinIO

### 1. Создание bucket

Убедитесь, что bucket `atg-uploads` создан в MinIO:

```bash
# Через MinIO Console (http://45.138.159.79:9001)
# Перейдите в раздел Buckets -> Create Bucket
# Имя: atg-uploads
# Region: us-east-1
```

### 2. Настройка CORS (важно!)

Для работы загрузки файлов напрямую из браузера необходимо настроить CORS на MinIO.

**Через MinIO Console:**
1. Перейдите в Settings -> CORS
2. Добавьте следующую конфигурацию:

```
AllowOrigin: http://localhost:5173, https://your-domain.com
AllowMethods: GET,PUT,POST,DELETE,HEAD
AllowHeaders: *
MaxAge: 3600
```

**Или через mc (MinIO Client):**
```bash
mc cors set public local/atg-uploads
```

### 3. Настройка политики доступа

Установите политику доступа для bucket:

```bash
# Через MinIO Console
# Перейдите в Buckets -> atg-uploads -> Access Policy
# Выберите: Public (read) или Custom
```

## Использование в админ-панели

### Загрузка файлов

1. Перейдите в админ-панель (`/admin`)
2. Откройте вкладку "Файлы"
3. Перетащите файлы в область загрузки или нажмите для выбора
4. Нажмите "Загрузить файлы"
5. Дождитесь завершения загрузки

### Просмотр файлов

Все загруженные файлы отображаются в виде карточек с информацией:
- Имя файла
- Размер
- Кнопки: Просмотр, Скачать, Удалить

### Функции

- **Загрузка**: Drag & Drop или выбор файлов
- **Просмотр**: Открытие файла в новой вкладке
- **Скачивание**: Скачивание файла
- **Удаление**: Удаление файла из MinIO и базы данных

## Ограничения

1. **Прямая загрузка**: В текущей реализации используется прямая загрузка в MinIO, что требует настройки CORS
2. **Список файлов**: Получение списка файлов требует доступа к базе данных Supabase
3. **Безопасность**: Для production рекомендуется:
   - Использовать presigned URLs для загрузки
   - Настроить бэкенд API для управления файлами
   - Внедрить авторизацию на уровне MinIO

## Будущие улучшения

- [ ] Добавить presigned URLs для загрузки
- [ ] Настроить авторизацию через MinIO API
- [ ] Добавить поиск и фильтрацию файлов
- [ ] Добавить превью изображений
- [ ] Добавить организацию файлов по папкам
- [ ] Добавить квоты на размер загружаемых файлов

## Тестирование

1. Загрузите тестовый файл
2. Проверьте, что файл появился в списке
3. Попробуйте открыть файл
4. Попробуйте скачать файл
5. Попробуйте удалить файл

## Troubleshooting

### Ошибка CORS при загрузке

**Решение**: Убедитесь, что CORS настроен правильно в MinIO

### Ошибка 403 при доступе к файлу

**Решение**: Проверьте политику доступа к bucket

### Ошибка подключения к MinIO

**Решение**: Проверьте, что MinIO доступен по адресу `http://45.138.159.79:9001`

