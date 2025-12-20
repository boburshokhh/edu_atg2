# 🔐 LDAP Аутентификация

## Обзор

Система поддерживает аутентификацию через LDAP/Active Directory. LDAP аутентификация интегрирована в Django бэкенд и работает прозрачно для фронтенда.

## Конфигурация

### Backend (Django)

Настройки LDAP находятся в файле `.env` (или `env.txt`) в директории `backend_django/`:

```env
# LDAP Authentication
LDAP_ENABLED=true
LDAP_SERVER=ldap://192.168.32.100:389
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_DN=cn=admin,dc=example,dc=com
LDAP_USER_PASSWORD=admin
LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
LDAP_USER_SEARCH_FILTER=(uid={username})
LDAP_GROUP_SEARCH_BASE=ou=groups,dc=example,dc=com
LDAP_REQUIRE_GROUP=
LDAP_USE_TLS=false
LDAP_TLS_CA_FILE=
```

#### Параметры конфигурации:

- **LDAP_ENABLED** - включить/выключить LDAP аутентификацию (true/false)
- **LDAP_SERVER** - адрес LDAP сервера (ldap:// или ldaps://)
- **LDAP_BASE_DN** - базовый DN для поиска
- **LDAP_USER_DN** - DN пользователя для подключения к LDAP (для поиска)
- **LDAP_USER_PASSWORD** - пароль для LDAP_USER_DN
- **LDAP_USER_SEARCH_BASE** - базовый DN для поиска пользователей
- **LDAP_USER_SEARCH_FILTER** - фильтр поиска пользователя (используйте {username} как плейсхолдер)
- **LDAP_GROUP_SEARCH_BASE** - базовый DN для поиска групп
- **LDAP_REQUIRE_GROUP** - обязательная группа для доступа (пусто = не требуется)
- **LDAP_USE_TLS** - использовать TLS (true/false)
- **LDAP_TLS_CA_FILE** - путь к файлу CA сертификата (опционально)

### Frontend

Настройки LDAP для фронтенда (опционально, для информации):

```env
# LDAP Authentication
VITE_LDAP_ENABLED=true
VITE_LDAP_SERVER=ldap://192.168.32.100:389
VITE_LDAP_BASE_DN=dc=example,dc=com
VITE_LDAP_USER_DN=cn=admin,dc=example,dc=com
VITE_LDAP_USER_PASSWORD=admin
VITE_LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
VITE_LDAP_USER_SEARCH_FILTER=(uid={username})
```

**Примечание**: Фронтенд не выполняет прямые LDAP запросы. Все аутентификация происходит через Django API.

## Установка

### 1. Установка зависимостей

```bash
cd backend_django
pip install -r requirements.txt
```

Требуется пакет `python-ldap==3.4.3`.

**Важно**: Для установки `python-ldap` могут потребоваться системные библиотеки:
- Ubuntu/Debian: `sudo apt-get install libldap2-dev libsasl2-dev`
- CentOS/RHEL: `sudo yum install openldap-devel`
- macOS: `brew install openldap`

### 2. Настройка переменных окружения

Скопируйте `env.txt` в `.env` и настройте параметры LDAP:

```bash
cp env.txt .env
# Отредактируйте .env и настройте LDAP параметры
```

### 3. Перезапуск сервера

После изменения настроек перезапустите Django сервер:

```bash
python manage.py runserver
```

## Как это работает

### Процесс аутентификации

1. **Пользователь вводит логин и пароль** на фронтенде
2. **Фронтенд отправляет запрос** на `/api/accounts/login/`
3. **Django бэкенд проверяет LDAP** (если `LDAP_ENABLED=true`):
   - Подключается к LDAP серверу
   - Ищет пользователя по фильтру `LDAP_USER_SEARCH_FILTER`
   - Проверяет пароль, пытаясь привязаться как пользователь
   - Проверяет членство в группе (если `LDAP_REQUIRE_GROUP` установлен)
4. **Если LDAP аутентификация успешна**:
   - Создает или обновляет пользователя в базе данных
   - Определяет роль пользователя на основе LDAP групп:
     - Группы `admin`, `administrators`, `admins` → роль `admin`
     - Группы `instructor`, `instructors`, `teachers` → роль `instructor`
     - Остальные → роль `user`
   - Генерирует JWT токены
5. **Если LDAP не включен или аутентификация не удалась**:
   - Пытается аутентифицировать через базу данных (обычная аутентификация)
6. **Возвращает JWT токены** пользователю

### Определение ролей из LDAP групп

Система автоматически определяет роль пользователя на основе его членства в LDAP группах:

- **Admin**: если пользователь в группах `admin`, `administrators`, `admins`
- **Instructor**: если пользователь в группах `instructor`, `instructors`, `teachers`
- **User**: по умолчанию

## Примеры конфигурации

### Active Directory

```env
LDAP_ENABLED=true
LDAP_SERVER=ldap://ad.example.com:389
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_DN=CN=Service Account,CN=Users,DC=example,DC=com
LDAP_USER_PASSWORD=ServiceAccountPassword
LDAP_USER_SEARCH_BASE=CN=Users,DC=example,DC=com
LDAP_USER_SEARCH_FILTER=(sAMAccountName={username})
LDAP_GROUP_SEARCH_BASE=CN=Users,DC=example,DC=com
LDAP_REQUIRE_GROUP=
LDAP_USE_TLS=false
```

### OpenLDAP

```env
LDAP_ENABLED=true
LDAP_SERVER=ldap://ldap.example.com:389
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_DN=cn=admin,dc=example,dc=com
LDAP_USER_PASSWORD=admin
LDAP_USER_SEARCH_BASE=ou=people,dc=example,dc=com
LDAP_USER_SEARCH_FILTER=(uid={username})
LDAP_GROUP_SEARCH_BASE=ou=groups,dc=example,dc=com
LDAP_REQUIRE_GROUP=
LDAP_USE_TLS=false
```

### LDAP с TLS

```env
LDAP_ENABLED=true
LDAP_SERVER=ldaps://ldap.example.com:636
LDAP_BASE_DN=dc=example,dc=com
LDAP_USER_DN=cn=admin,dc=example,dc=com
LDAP_USER_PASSWORD=admin
LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com
LDAP_USER_SEARCH_FILTER=(uid={username})
LDAP_GROUP_SEARCH_BASE=ou=groups,dc=example,dc=com
LDAP_REQUIRE_GROUP=
LDAP_USE_TLS=true
LDAP_TLS_CA_FILE=/path/to/ca.crt
```

## Отладка

### Логирование

LDAP операции логируются в Django логах. Убедитесь, что уровень логирования настроен:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.accounts.ldap_utils': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Тестирование подключения

Для тестирования LDAP подключения можно использовать Python скрипт:

```python
from apps.accounts.ldap_utils import authenticate_ldap

result = authenticate_ldap('testuser', 'testpassword')
if result:
    print(f"Success! User: {result}")
else:
    print("Authentication failed")
```

## Безопасность

### Рекомендации

1. **Используйте TLS/SSL** для LDAP подключений в продакшене
2. **Ограничьте права** LDAP пользователя для поиска (LDAP_USER_DN)
3. **Используйте отдельный сервисный аккаунт** для LDAP подключений
4. **Не храните пароли** в открытом виде в `.env` файле
5. **Используйте переменные окружения** или секреты для паролей

### Обработка ошибок

Система обрабатывает следующие ошибки LDAP:
- Неверные учетные данные
- Пользователь не найден
- Пользователь не в требуемой группе
- Проблемы с подключением к LDAP серверу
- Ошибки TLS/SSL

Все ошибки логируются, но не раскрывают детали для безопасности.

## Миграция пользователей

При первой LDAP аутентификации пользователь автоматически создается в базе данных с информацией из LDAP:
- `username` - из LDAP
- `full_name` - из атрибутов `cn`, `givenName`, `sn`
- `email` - из атрибута `mail`
- `role` - определяется из групп LDAP

При последующих входах информация пользователя обновляется из LDAP, если она отсутствует в базе данных.

## Отключение LDAP

Для отключения LDAP аутентификации:

```env
LDAP_ENABLED=false
```

После этого система будет использовать только аутентификацию через базу данных.

---

**Дата создания**: 2025-01-23  
**Версия**: 1.0

