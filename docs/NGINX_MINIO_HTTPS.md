# Настройка HTTPS для MinIO через Nginx

## ✅ Текущая конфигурация

MinIO настроен для работы через HTTPS с Nginx reverse proxy.

### Параметры подключения:
- **Endpoint**: `https://minio.dmed.gubkin.uz`
- **Порт**: 443 (HTTPS, стандартный)
- **MinIO внутренний порт**: 9001 (проксируется через Nginx)
- **SSL сертификат**: Let's Encrypt

## 🔧 Конфигурация Nginx (актуальная)

### HTTP → HTTPS редирект

```nginx
server {
    listen 80;
    server_name minio.dmed.gubkin.uz;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://minio.dmed.gubkin.uz$request_uri;
    }
}
```

### HTTPS конфигурация (основной порт 9001)

```nginx
server {
    listen 443 ssl http2;
    server_name minio.dmed.gubkin.uz;

    # Let's Encrypt SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/minio.dmed.gubkin.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/minio.dmed.gubkin.uz/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Максимальный размер загружаемых файлов
    client_max_body_size 10G;

    # Основное проксирование на MinIO (порт 9001)
    location / {
        proxy_pass http://127.0.0.1:9001;
        proxy_http_version 1.1;

        # Пробрасываем все необходимые заголовки
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Для поддержки Range-запросов (стриминг видео)
        proxy_set_header Range $http_range;
        proxy_set_header If-Range $http_if_range;
        proxy_pass_header Content-Range;

        # Для WebSocket / UI обновлений (консоль MinIO)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Таймауты и буферизация
        proxy_read_timeout 300s;
        proxy_request_buffering off;

        # Чтобы Nginx не кэшировал частичные ответы
        proxy_buffering off;
    }

    # Альтернативный путь для MinIO консоли
    location /minio/ {
        rewrite ^/minio(/.*)$ $1 break;
        proxy_pass http://127.0.0.1:9001/;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }
}
```

### Проксирование порта 9000 (S3 API)

**Важно**: Добавьте этот блок отдельно, не трогая существующую конфигурацию для порта 9001. Они будут работать параллельно и не мешать друг другу.

**Решение**: Добавьте location блок для порта 9000 в существующий server блок для порта 9001. Это позволит им работать вместе без конфликтов.

Добавьте этот location блок в существующий server блок (после блока для порта 9001):

```nginx
# Добавьте этот location блок в существующий server блок для порта 9001
# Разместите его после location /minio/ блока

# Проксирование S3 API (порт 9000) через путь /s3/
location /s3/ {
    rewrite ^/s3/(.*)$ /$1 break;
    proxy_pass http://127.0.0.1:9000;
    proxy_http_version 1.1;

    # Пробрасываем все необходимые заголовки
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Для поддержки Range-запросов (стриминг видео)
    proxy_set_header Range $http_range;
    proxy_set_header If-Range $http_if_range;
    proxy_pass_header Content-Range;

    # Таймауты и буферизация
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    proxy_request_buffering off;

    # Отключение буферизации для streaming
    proxy_buffering off;
    
    # Важно для S3 API
    proxy_set_header Connection "";
    chunked_transfer_encoding off;
}

# Или, если нужен прямой доступ к порту 9000 без префикса /s3/
# Используйте отдельный location с более высоким приоритетом
location ~ ^/(atgedu|uploads|videos|stations)/ {
    proxy_pass http://127.0.0.1:9000;
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_set_header Range $http_range;
    proxy_set_header If-Range $http_if_range;
    proxy_pass_header Content-Range;

    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    proxy_request_buffering off;
    proxy_buffering off;
    proxy_set_header Connection "";
    chunked_transfer_encoding off;
}
```

**Альтернативный вариант**: Если нужен полностью отдельный server блок (не рекомендуется, так как будет конфликт на одном порту), можно использовать разные поддомены:

```nginx
# Отдельный поддомен для S3 API (например, s3.minio.dmed.gubkin.uz)
server {
    listen 443 ssl http2;
    server_name s3.minio.dmed.gubkin.uz;

    ssl_certificate /etc/letsencrypt/live/minio.dmed.gubkin.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/minio.dmed.gubkin.uz/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 10G;

    location / {
        proxy_pass http://127.0.0.1:9000;
        # ... остальные настройки как выше
    }
}
```

**Рекомендация**: Используйте первый вариант с location блоками в одном server блоке - это проще и надежнее.

### Ключевые особенности конфигурации:

✅ **Поддержка Range-запросов** - для стриминга видео по частям  
✅ **Отключена буферизация** - для потоковой передачи данных  
✅ **WebSocket поддержка** - для MinIO консоли (порт 9001)  
✅ **Большие файлы** - до 10GB  
✅ **Let's Encrypt** - автоматическое обновление сертификатов  
✅ **Два порта** - 9001 (консоль) и 9000 (S3 API) через HTTPS

## ✅ Обновленная конфигурация приложения

Конфигурация обновлена для работы через HTTPS:

### `src/services/minioService.js`
```javascript
const MINIO_CONFIG = {
  endpoint: 'https://minio.dmed.gubkin.uz',
  region: 'us-east-1',
  credentials: {
    accessKeyId: 'admin',
    secretAccessKey: '1234bobur$'
  },
  forcePathStyle: true,
  tls: true // HTTPS через Nginx (порт 443)
}
```

**Важно**: Endpoint указывается без порта, так как используется стандартный HTTPS порт 443.

## 🧪 Тестирование

### Проверка доступности

```bash
# Проверка доступности через HTTPS
curl -I https://minio.dmed.gubkin.uz

# Проверка через тестовый скрипт
npm run test:minio
```

### Ожидаемый результат

Тест должен показать:
- ✅ Подключение к MinIO успешно
- ✅ Получение списка файлов работает
- ✅ Presigned URLs генерируются корректно
- ✅ Видео файлы доступны для стриминга

## 🔍 Проверка работы

1. **Проверьте SSL сертификат**:
   ```bash
   openssl s_client -connect minio.dmed.gubkin.uz:443 -servername minio.dmed.gubkin.uz
   ```

2. **Проверьте проксирование**:
   - Запросы к `https://minio.dmed.gubkin.uz` должны проксироваться на `http://127.0.0.1:9001` (консоль)
   - Запросы к `https://minio.dmed.gubkin.uz:9000` должны проксироваться на `http://127.0.0.1:9000` (S3 API)

3. **Проверьте Range-запросы** (для стриминга):
   ```bash
   curl -I -H "Range: bytes=0-1023" https://minio.dmed.gubkin.uz/atgedu/video.mp4
   ```
   Должен вернуть `206 Partial Content`

## 📝 Примечания

- MinIO работает на внутренних портах **9000** (S3 API) и **9001** (консоль)
- Nginx проксирует HTTPS (443) → HTTP (127.0.0.1:9000/9001)
- Все запросы идут через HTTPS, что обеспечивает безопасность
- Range-запросы поддерживаются для стриминга видео
- Приложение использует endpoint без порта: `https://minio.dmed.gubkin.uz` (стандартный HTTPS порт 443)

## 🔧 Настройка Nginx для порта 9000

После добавления конфигурации для порта 9000:

1. **Проверьте конфигурацию**:
   ```bash
   sudo nginx -t
   ```

2. **Перезагрузите Nginx**:
   ```bash
   sudo systemctl reload nginx
   ```

3. **Проверьте доступность**:
   ```bash
   curl -I https://minio.dmed.gubkin.uz
   ```
