# Настройка стриминга видео в MinIO

## Обзор

Для обеспечения стриминга видео по частям (как на YouTube) необходимо настроить MinIO для поддержки HTTP Range requests. Это позволяет браузеру загружать только необходимые части видео, а не весь файл целиком.

## Требования к MinIO

### 1. CORS настройки

MinIO должен быть настроен для разрешения:
- Range запросов
- Cross-Origin запросов
- Правильных заголовков

### 2. Настройка CORS через MinIO Console

1. Зайдите в MinIO Console (обычно `http://your-minio-server:9001`)
2. Перейдите в **Buckets** → **uploads** → **Access Policy**
3. Добавьте CORS правила:

```json
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["Content-Range", "Content-Length", "ETag", "Accept-Ranges"],
    "MaxAgeSeconds": 3600
  }
]
```

### 3. Настройка через MinIO CLI (mc)

```bash
# Установка mc (если еще не установлен)
# Linux/Mac:
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Создание alias
./mc alias set myminio http://45.138.159.79:9000 admin 1234bobur$

# Настройка CORS для bucket
./mc cors set download myminio/uploads
```

### 4. Настройка CORS через mc (автоматически)

Создайте файл `cors.json`:
```json
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD", "OPTIONS"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["Content-Range", "Content-Length", "ETag", "Accept-Ranges", "Content-Type"],
    "MaxAgeSeconds": 3600
  }
]
```

Затем выполните:
```bash
mc cors import myminio/uploads < cors.json
```

## Как это работает

### HTTP Range Requests

Когда браузер загружает видео через HTML5 `<video>` элемент, он автоматически отправляет Range запросы:

```
GET /bucket/video.mp4 HTTP/1.1
Host: files.dormitory.gubkin.uz
Range: bytes=0-1023999
```

MinIO отвечает:
```
HTTP/1.1 206 Partial Content
Content-Range: bytes 0-1023999/52428800
Content-Length: 1024000
Accept-Ranges: bytes
```

### Преимущества

1. **Быстрый старт воспроизведения**: Плеер начинает воспроизведение сразу после загрузки metadata (обычно первые ~100KB)
2. **Оптимизация трафика**: Загружаются только просматриваемые части видео
3. **Перемотка без ожидания**: При перемотке загружается только нужный сегмент
4. **Экономия памяти**: Видео не загружается полностью в память

## Оптимизация MP4 файлов

Для лучшего стриминга MP4 файлы должны иметь структуру:
- **moov atom в начале файла** (fast start)
- Это позволяет начать воспроизведение сразу, не загружая весь файл

### Конвертация существующих видео

Используйте ffmpeg для оптимизации:

```bash
# Конвертация с fast start (moov atom в начале)
ffmpeg -i input.mp4 -c copy -movflags +faststart output.mp4

# Или с перекодированием (если нужно)
ffmpeg -i input.mp4 -c:v libx264 -profile:v high -level 4.0 -c:a aac -movflags +faststart output.mp4
```

## Альтернатива: HLS стриминг

Для еще лучшего стриминга (как на YouTube) можно конвертировать видео в HLS формат:

### Конвертация в HLS

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -c:a aac \
  -f hls \
  -hls_time 10 \
  -hls_playlist_type vod \
  -hls_segment_filename "video_%03d.ts" \
  playlist.m3u8
```

Это создаст:
- `playlist.m3u8` - плейлист
- `video_000.ts`, `video_001.ts`, etc. - сегменты видео

Загрузите все файлы в MinIO, структура:
```
uploads/
  lesson1/
    playlist.m3u8
    video_000.ts
    video_001.ts
    ...
```

## Настройка кода

Код уже настроен для поддержки:
1. ✅ HTTP Range requests для MP4/WebM (автоматически через HTML5 video)
2. ✅ HLS стриминг через HLS.js
3. ✅ Presigned URLs с правильными заголовками
4. ✅ Оптимизированная загрузка (preload="metadata")

## Проверка работы

### Тест Range запросов

```bash
# Запрос первых 1024 байт
curl -I -H "Range: bytes=0-1023" "https://files.dormitory.gubkin.uz/uploads/video.mp4?presigned-url"

# Должен вернуть:
# HTTP/1.1 206 Partial Content
# Content-Range: bytes 0-1023/52428800
# Accept-Ranges: bytes
```

### Проверка в браузере

1. Откройте DevTools → Network
2. Воспроизведите видео
3. Проверьте запросы к видео - должны видеть Range запросы:
   - `Range: bytes=0-...`
   - Ответ `206 Partial Content`

## Troubleshooting

### Проблема: Видео не начинает воспроизводиться сразу

**Решение**: 
- Проверьте CORS настройки MinIO
- Убедитесь, что presigned URLs поддерживают Range запросы
- Конвертируйте видео с `faststart` флагом

### Проблема: Ошибка CORS

**Решение**:
- Проверьте CORS правила в MinIO
- Убедитесь, что `ExposeHeaders` содержит `Content-Range`

### Проблема: Видео загружается полностью

**Решение**:
- Убедитесь, что MinIO возвращает `Accept-Ranges: bytes`
- Проверьте, что в видео `preload="metadata"` (не `auto`)
- Проверьте структуру MP4 файла (moov atom должен быть в начале)

## Дополнительные оптимизации

1. **CDN**: Используйте CDN перед MinIO для кеширования
2. **Адаптивное качество**: Используйте HLS с разными битрейтами
3. **Сжатие**: Убедитесь, что видео правильно сжато
4. **Кеширование**: Настройте кеширование на уровне MinIO/CDN

