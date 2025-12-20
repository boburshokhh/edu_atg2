# Проверка сохранения данных станций в БД

## Как проверить, что все данные сохраняются правильно

### 1. Создание станции через админ-панель

1. Откройте админ-панель → вкладка "Станции"
2. Нажмите "Добавить станцию"
3. Заполните форму:
   - **Основная информация**: название, описание, все поля
   - **Загрузите изображение станции** (drag & drop)
   - **Загрузите техническую карту** (если есть)
   - **Добавьте оборудование** (минимум 1 элемент)
   - **Добавьте спецификации** (минимум 1 элемент)
   - **Добавьте системы безопасности** с характеристиками (минимум 1 элемент)
   - **Добавьте источники газоснабжения** (минимум 1 элемент)
4. Нажмите "Создать"

### 2. Проверка в PostgreSQL

Выполните следующие SQL запросы для проверки сохранения данных:

```sql
-- 1. Проверка основной информации станции
SELECT 
    id, name, short_name, description, 
    image, tech_map_image, power, status,
    location, type, design_capacity
FROM stations 
WHERE id = <ID_СТАНЦИИ>
ORDER BY id DESC 
LIMIT 1;

-- 2. Проверка оборудования
SELECT 
    id, station_id, name, model, manufacturer,
    quantity, power, description, order_index
FROM station_equipment 
WHERE station_id = <ID_СТАНЦИИ>
ORDER BY order_index;

-- 3. Проверка спецификаций
SELECT 
    id, station_id, category, value, unit,
    description, order_index
FROM station_specifications 
WHERE station_id = <ID_СТАНЦИИ>
ORDER BY order_index;

-- 4. Проверка систем безопасности
SELECT 
    id, station_id, name, description,
    manufacturer, order_index
FROM station_safety_systems 
WHERE station_id = <ID_СТАНЦИИ>
ORDER BY order_index;

-- 5. Проверка характеристик систем безопасности
SELECT 
    ssf.id, ssf.safety_system_id, sss.name as system_name,
    ssf.feature_name, ssf.order_index
FROM station_safety_system_features ssf
JOIN station_safety_systems sss ON ssf.safety_system_id = sss.id
WHERE sss.station_id = <ID_СТАНЦИИ>
ORDER BY ssf.order_index;

-- 6. Проверка источников газоснабжения
SELECT 
    id, station_id, source_name, order_index
FROM station_gas_supply_sources 
WHERE station_id = <ID_СТАНЦИИ>
ORDER BY order_index;

-- 7. Полная проверка всех данных станции
SELECT 
    s.id, s.name, s.short_name,
    COUNT(DISTINCT eq.id) as equipment_count,
    COUNT(DISTINCT spec.id) as specs_count,
    COUNT(DISTINCT safety.id) as safety_systems_count,
    COUNT(DISTINCT gas.id) as gas_sources_count,
    s.image, s.tech_map_image
FROM stations s
LEFT JOIN station_equipment eq ON eq.station_id = s.id
LEFT JOIN station_specifications spec ON spec.station_id = s.id
LEFT JOIN station_safety_systems safety ON safety.station_id = s.id
LEFT JOIN station_gas_supply_sources gas ON gas.station_id = s.id
WHERE s.id = <ID_СТАНЦИИ>
GROUP BY s.id, s.name, s.short_name, s.image, s.tech_map_image;
```

### 3. Проверка изображений в MinIO

1. Откройте MinIO Console (обычно http://192.168.32.100:9001)
2. Перейдите в bucket `atgedu`
3. Проверьте наличие файлов:
   - **Изображение станции**: должно быть в папке `stations/` (например: `stations/1234567890-WKC1.jpg`)
   - **Техническая карта**: должна быть в папке `tex_kart/` (например: `tex_kart/1234567890-map.jpg`)
4. Проверьте, что путь в БД (поле `image` в таблице `stations`) соответствует пути в MinIO

### 4. Проверка через API

```bash
# Получить информацию о станции
curl -X GET "http://localhost:8000/api/stations/<ID>" \
  -H "Authorization: Bearer <TOKEN>"

# Проверить оборудование
curl -X GET "http://localhost:8000/api/stations/<ID>/equipment" \
  -H "Authorization: Bearer <TOKEN>"

# Проверить спецификации
curl -X GET "http://localhost:8000/api/stations/<ID>/specs" \
  -H "Authorization: Bearer <TOKEN>"

# Проверить системы безопасности
curl -X GET "http://localhost:8000/api/stations/<ID>/safety" \
  -H "Authorization: Bearer <TOKEN>"

# Проверить источники газоснабжения
curl -X GET "http://localhost:8000/api/stations/<ID>/gas-sources" \
  -H "Authorization: Bearer <TOKEN>"
```

### 5. Типичные проблемы и решения

#### Проблема: Изображение не сохраняется
- **Причина**: Файл не загружен в MinIO или путь не сохранен в БД
- **Решение**: 
  1. Проверьте, что файл загружен в MinIO
  2. Проверьте поле `image` в таблице `stations` - должно содержать путь к файлу в MinIO

#### Проблема: Связанные данные не сохраняются
- **Причина**: Ошибка при сохранении или отсутствие ID станции
- **Решение**:
  1. Проверьте консоль браузера на ошибки
  2. Убедитесь, что станция создана и имеет ID
  3. Проверьте логи Django на ошибки

#### Проблема: Данные дублируются при редактировании
- **Причина**: Неправильная логика удаления старых данных
- **Решение**: Проверьте, что при редактировании удаляются данные, которых нет в новой версии

### 6. Формат путей к изображениям

- **В БД**: `stations/1234567890-filename.jpg` или `tex_kart/1234567890-filename.jpg`
- **Старый формат**: Если указано просто имя файла (например: `WKC1.jpg`), система ищет его в папке `stations/`
- **Отображение**: Используется presigned URL из MinIO для безопасного доступа

### 7. Проверка целостности данных

Выполните проверку целостности данных:

```sql
-- Проверка на отсутствующие связи
SELECT 'Equipment without station' as issue, COUNT(*) as count
FROM station_equipment eq
LEFT JOIN stations s ON eq.station_id = s.id
WHERE s.id IS NULL

UNION ALL

SELECT 'Specs without station', COUNT(*)
FROM station_specifications spec
LEFT JOIN stations s ON spec.station_id = s.id
WHERE s.id IS NULL

UNION ALL

SELECT 'Safety without station', COUNT(*)
FROM station_safety_systems safety
LEFT JOIN stations s ON safety.station_id = s.id
WHERE s.id IS NULL

UNION ALL

SELECT 'Features without safety system', COUNT(*)
FROM station_safety_system_features feat
LEFT JOIN station_safety_systems safety ON feat.safety_system_id = safety.id
WHERE safety.id IS NULL

UNION ALL

SELECT 'Gas sources without station', COUNT(*)
FROM station_gas_supply_sources gas
LEFT JOIN stations s ON gas.station_id = s.id
WHERE s.id IS NULL;
```

Все запросы должны вернуть 0 записей.

