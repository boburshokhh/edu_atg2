# Интеграция админ-панели со станциями

## Реализованный функционал

### 1. Загрузка изображений станций

- **Изображение станции**: загружается в MinIO в папку `stations/`
- **Техническая карта**: загружается в MinIO в папку `tex_kart/`
- Путь к изображению сохраняется в поле `image` таблицы `stations`
- Путь к технической карте сохраняется в поле `tech_map_image` таблицы `stations`

### 2. Сохранение данных в БД

Все данные станции сохраняются через Django REST API:

#### Основная информация станции
- Сохраняется в таблицу `stations`
- Поля: name, short_name, description, image, tech_map_image, power, commission_date, status, location, type, design_capacity, gas_pressure, distance_from_border, pipeline_diameter, input_pressure, output_pressure, parallel_lines

#### Оборудование
- Сохраняется в таблицу `station_equipment`
- Связь через `station_id`
- Автоматическое удаление при редактировании (если удалено из формы)

#### Спецификации
- Сохраняется в таблицу `station_specifications`
- Связь через `station_id`
- Автоматическое удаление при редактировании

#### Системы безопасности
- Сохраняется в таблицу `station_safety_systems`
- Характеристики сохраняются в `station_safety_system_features`
- Связь через `station_id` и `safety_system_id`

#### Источники газоснабжения
- Сохраняется в таблицу `station_gas_supply_sources`
- Связь через `station_id`

### 3. Проверка сохранения данных

Для проверки правильности сохранения данных:

1. **Создайте станцию через админ-панель**
   - Заполните все поля
   - Загрузите изображение
   - Добавьте оборудование, спецификации, системы безопасности
   - Сохраните

2. **Проверьте в БД:**
   ```sql
   -- Проверка основной информации
   SELECT * FROM stations WHERE id = <station_id>;
   
   -- Проверка оборудования
   SELECT * FROM station_equipment WHERE station_id = <station_id>;
   
   -- Проверка спецификаций
   SELECT * FROM station_specifications WHERE station_id = <station_id>;
   
   -- Проверка систем безопасности
   SELECT * FROM station_safety_systems WHERE station_id = <station_id>;
   SELECT * FROM station_safety_system_features WHERE safety_system_id IN (
     SELECT id FROM station_safety_systems WHERE station_id = <station_id>
   );
   
   -- Проверка источников газоснабжения
   SELECT * FROM station_gas_supply_sources WHERE station_id = <station_id>;
   ```

3. **Проверьте изображения в MinIO:**
   - Изображение должно быть в bucket `atgedu` в папке `stations/`
   - Техническая карта должна быть в папке `tex_kart/`
   - Путь в БД должен соответствовать пути в MinIO

### 4. Использование

#### Создание станции
1. Откройте админ-панель → вкладка "Станции"
2. Нажмите "Добавить станцию"
3. Заполните форму:
   - Основная информация (вкладка "Основная информация")
   - Загрузите изображение станции (drag & drop или выбор файла)
   - Загрузите техническую карту (если есть)
   - Добавьте оборудование (вкладка "Оборудование")
   - Добавьте спецификации (вкладка "Спецификации")
   - Добавьте системы безопасности с характеристиками (вкладка "Системы безопасности")
   - Добавьте источники газоснабжения (вкладка "Источники газоснабжения")
4. Нажмите "Создать"

#### Редактирование станции
1. В таблице станций нажмите "Редактировать"
2. Внесите изменения
3. При необходимости загрузите новое изображение (старое будет заменено)
4. Нажмите "Сохранить"

### 5. API Endpoints

Все endpoints требуют аутентификации администратора (JWT token с ролью `admin`):

- `POST /api/stations/create/` - создание станции
- `PUT /api/stations/<id>/update/` - обновление станции
- `DELETE /api/stations/<id>/delete/` - удаление станции
- `POST /api/stations/<id>/equipment/create/` - добавление оборудования
- `PUT /api/stations/<id>/equipment/<equipment_id>/update/` - обновление оборудования
- `DELETE /api/stations/<id>/equipment/<equipment_id>/delete/` - удаление оборудования
- Аналогичные endpoints для specs, safety, gas-sources

### 6. Формат данных изображений

- **В БД**: сохраняется путь к объекту в MinIO (например: `stations/1234567890-WKC1.jpg`)
- **Отображение**: используется presigned URL из MinIO для безопасного доступа
- **Старый формат**: если изображение указано как просто имя файла (например: `WKC1.jpg`), система автоматически ищет его в папке `stations/`

### 7. Импорт данных

Для импорта данных из `stationsData.js`:

```bash
cd backend_django
.\venv\Scripts\Activate.ps1
python manage.py import_stations --file ../src/data/stationsData.js --update
```

**Примечание**: Убедитесь, что путь к файлу указан правильно относительно директории `backend_django`.

