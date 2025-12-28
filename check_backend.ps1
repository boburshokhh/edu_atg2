# Скрипт для диагностики проблемы 502 Bad Gateway (PowerShell)

Write-Host "=== Проверка статуса контейнеров ===" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n=== Проверка логов backend (последние 50 строк) ===" -ForegroundColor Cyan
docker-compose logs --tail=50 backend

Write-Host "`n=== Проверка доступности backend изнутри frontend ===" -ForegroundColor Cyan
$result = docker-compose exec -T frontend wget -q -O- http://backend:8000/health 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend доступен из frontend контейнера" -ForegroundColor Green
    Write-Host $result
} else {
    Write-Host "❌ ОШИБКА: Backend недоступен из frontend контейнера" -ForegroundColor Red
    Write-Host $result
}

Write-Host "`n=== Проверка health endpoint напрямую ===" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend доступен на localhost:8000" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "❌ ОШИБКА: Backend недоступен на localhost:8000" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "`n=== Проверка health endpoint через nginx ===" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend доступен через nginx" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "❌ ОШИБКА: Backend недоступен через nginx" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host "`n=== Проверка наличия .env файла ===" -ForegroundColor Cyan
if (Test-Path "backend_django\.env") {
    Write-Host "✅ Файл backend_django\.env существует" -ForegroundColor Green
} else {
    Write-Host "❌ Файл backend_django\.env НЕ существует!" -ForegroundColor Red
    Write-Host "   Создайте его: Copy-Item backend_django\env.txt backend_django\.env" -ForegroundColor Yellow
}

Write-Host "`n=== Проверка переменных окружения PostgreSQL ===" -ForegroundColor Cyan
$postgresVars = docker-compose exec -T backend env | Select-String "POSTGRES"
if ($postgresVars) {
    Write-Host $postgresVars
} else {
    Write-Host "Переменные POSTGRES не найдены" -ForegroundColor Yellow
}

Write-Host "`n=== Проверка переменных окружения MinIO ===" -ForegroundColor Cyan
$minioVars = docker-compose exec -T backend env | Select-String "MINIO"
if ($minioVars) {
    Write-Host $minioVars
} else {
    Write-Host "Переменные MINIO не найдены" -ForegroundColor Yellow
}

Write-Host "`n=== Проверка подключения к PostgreSQL ===" -ForegroundColor Cyan
$pgCheck = docker-compose exec -T backend python -c @"
import os
import sys
try:
    import psycopg
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = int(os.getenv('POSTGRES_PORT', '5432'))
    db = os.getenv('POSTGRES_DB', 'atg_edu')
    user = os.getenv('POSTGRES_USER', 'admin')
    pwd = os.getenv('POSTGRES_PASSWORD', 'admin')
    c = psycopg.connect(host=host, port=port, dbname=db, user=user, password=pwd, connect_timeout=3)
    c.close()
    print('✅ Подключение к PostgreSQL успешно')
except Exception as e:
    print(f'❌ Ошибка подключения к PostgreSQL: {e}')
    sys.exit(1)
"@
if ($LASTEXITCODE -eq 0) {
    Write-Host $pgCheck -ForegroundColor Green
} else {
    Write-Host "❌ Не удалось проверить подключение к PostgreSQL" -ForegroundColor Red
    Write-Host $pgCheck
}

Write-Host "`n=== Диагностика завершена ===" -ForegroundColor Cyan

