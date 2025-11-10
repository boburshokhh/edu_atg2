# Настройка MinIO - Инструкция

## ✅ Выполненная конфигурация

### Параметры подключения
- **Endpoint**: `http://45.138.159.79:9000`
- **Access Key (логин)**: `admin`
- **Secret Key (пароль)**: `1234bobur$`
- **Bucket**: `uploads`
- **Region**: `us-east-1`

### Установленные пакеты
```bash
npm install @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
```

## 🔧 Что нужно настроить в MinIO

### 1. Создать bucket

1. Откройте MinIO Console: http://45.138.159.79:9000
2. Войдите с учетными данными:
   - Access Key: `admin`
   - Secret Key: `1234bobur$`
3. Перейдите в **Buckets** → **Create Bucket**
4. Имя bucket: `uploads`
5. Нажмите **Create**

### 2. Настроить CORS для bucket

Для работы загрузки из браузера нужно настроить CORS:

**Через MinIO Console:**
1. Перейдите в **Administrator** → **Settings** → **API**
2. Найдите **CORS Allowed Origins**
3. Добавьте:
```
http://localhost:3000
http://localhost:3001
http://localhost:5173
https://your-domain.com
```

**Или через mc (MinIO Client):**
```bash
mc alias set myminio http://45.138.159.79:9000 admin 1234bobur$
mc anonymous set-json policy.json myminio/uploads
```

Содержимое `policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::uploads/*"]
    }
  ]
}
```

### 3. Настроить Access Policy для bucket

1. Перейдите в **Buckets** → `uploads` → **Anonymous**
2. Выберите **Custom** или **Public**
3. Добавьте следующую политику:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::uploads",
        "arn:aws:s3:::uploads/*"
      ]
    }
  ]
}
```

## 📊 Создать таблицу в Supabase (опционально)

Таблица для хранения метаданных файлов:

```sql
CREATE TABLE IF NOT EXISTS files (
  id BIGSERIAL PRIMARY KEY,
  object_name TEXT NOT NULL UNIQUE,
  file_name TEXT NOT NULL,
  original_name TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  file_type TEXT,
  file_url TEXT NOT NULL,
  uploaded_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_files_object_name ON files(object_name);
CREATE INDEX idx_files_uploaded_at ON files(uploaded_at DESC);

ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Политика для чтения
CREATE POLICY "Allow public read" ON files
  FOR SELECT USING (true);

-- Политика для администраторов
CREATE POLICY "Allow admin all" ON files
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid() AND users.role = 'admin'
    )
  );
```

## 🧪 Тестирование

### 1. Проверка подключения

Откройте консоль браузера в админ-панели и выполните:
```javascript
import minioService from '@/services/minioService'

// Проверка списка файлов
const files = await minioService.listFiles()
console.log('Файлы:', files)
```

### 2. Тест загрузки

1. Откройте админ-панель: http://localhost:3001/admin
2. Перейдите на вкладку "Файлы"
3. Перетащите тестовый файл
4. Нажмите "Загрузить файлы"
5. Проверьте, что файл появился в списке

### 3. Проверка в MinIO Console

1. Откройте http://45.138.159.79:9000
2. Войдите (admin / 1234bobur$)
3. Перейдите в Buckets → uploads
4. Убедитесь, что файл загружен

## 🔒 Безопасность

### Для Production:

1. **Измените credentials** в `.env`:
```env
VITE_MINIO_ENDPOINT=http://45.138.159.79:9000
VITE_MINIO_ACCESS_KEY=your-access-key
VITE_MINIO_SECRET_KEY=your-secret-key
VITE_MINIO_BUCKET=uploads
```

2. **Обновите** `src/services/minioService.js`:
```javascript
const MINIO_CONFIG = {
  endpoint: import.meta.env.VITE_MINIO_ENDPOINT,
  credentials: {
    accessKeyId: import.meta.env.VITE_MINIO_ACCESS_KEY,
    secretAccessKey: import.meta.env.VITE_MINIO_SECRET_KEY
  },
  ...
}
```

3. **Используйте HTTPS** для production

4. **Ограничьте CORS** только для вашего домена

## ✨ Возможности

После настройки доступны:
- ✅ Загрузка файлов (drag & drop)
- ✅ Получение списка файлов из MinIO
- ✅ Просмотр файлов
- ✅ Скачивание файлов
- ✅ Удаление файлов
- ✅ Отображение размера и метаданных
- ✅ Прогресс загрузки

## 🐛 Troubleshooting

### Ошибка: "Access Denied"
**Решение**: Проверьте Access Policy bucket'а

### Ошибка: "CORS policy"
**Решение**: Настройте CORS в MinIO Settings

### Ошибка: "Network Error"
**Решение**: Проверьте доступность MinIO на порту 9000

### Файлы не отображаются
**Решение**: 
1. Проверьте credentials в minioService.js
2. Убедитесь, что bucket `uploads` существует
3. Проверьте консоль браузера на ошибки

## 📝 Логи

Для отладки проверьте:
1. **Консоль браузера** (F12 → Console)
2. **Network tab** (F12 → Network) - смотрите запросы к MinIO
3. **MinIO Server logs** - на сервере MinIO

## 🎯 Следующие шаги

1. Создайте bucket `uploads`
2. Настройте CORS
3. Настройте Access Policy
4. Протестируйте загрузку файла
5. (Опционально) Создайте таблицу в Supabase

После выполнения всех шагов система будет полностью готова к работе!

