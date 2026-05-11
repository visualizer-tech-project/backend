# EduMap — Интерактивная карта учебных курсов

**EduMap** — это веб-сервис для визуализации учебных планов в виде интерактивного графа. Проект помогает студентам, абитуриентам и администраторам понимать структуру образовательных программ, видеть связи между курсами (пререквизиты) и осознанно планировать индивидуальную траекторию обучения.

## Состав команды и распределение ролей

- **Бэкенд-разработчики:**
    - @Amir_Khubeev
    - @Ka1ser67
- **Фронтенд-разработчики:**
    - @redwv
    - @anvarshigapov
    - @radrikk

## Инструкция по запуску проекта

### Предварительные требования

uv

### Шаги для запуска

1. **Клонируйте репозиторий**
2. **uv sync**
3. **uv run fastapi dev main.py**


## Запуск через Docker Compose

### Требования
- Docker Desktop (включает Docker и Docker Compose)
```bash
    docker-compose up -d --build
```

### Переменные окружения

Для настройки приложения создайте файл `.env` на основе `.env.example`:

### Переменные окружения

Для настройки приложения используйте файл `.env`.

| Название переменной | Тип | Описание | Значение по умолчанию |
|---------------------|-----|----------|----------------------|
| DB__SCHEMA | string | Драйвер для подключения | postgresql+asyncpg |
| DB__HOST | string | Хост базы данных | db |
| DB__PORT | int | Порт базы данных | 5432 |
| DB__USER | string | Имя пользователя базы данных | postgres |
| DB__PASSWORD | string | Пароль пользователя базы данных | |
| DB__NAME | string | Имя базы данных | edumap |
| AUTH__JWT_SECRET_KEY | string | Секретный ключ для JWT (мин. 32 символа) | |
| AUTH__JWT_ALGORITHM | string | Алгоритм шифрования JWT | HS256 |
| AUTH__ACCESS_TOKEN_EXPIRE_MINUTES | int | Время жизни access токена в минутах | 15 |
| AUTH__REFRESH_TOKEN_EXPIRE_DAYS | int | Время жизни refresh токена в днях | 7 |
| RBAC__ADMIN_EMAIL | string | Email администратора | admin@example.com |
| RBAC__ADMIN_PASSWORD | string | Пароль администратора | |
| RBAC__ADMIN_FIRST_NAME | string | Имя администратора | Admin |
| RBAC__ADMIN_LAST_NAME | string | Фамилия администратора | User |
| RBAC__ADMIN_ROLE | string | Роль администратора | admin |
| RBAC__PUBLIC_ROLE | string | Публичная роль по умолчанию | public |
| DEBUG | bool | Режим отладки | false |

Для запуска скопируйте `.env.example` в `.env` и заполните значения


### Миграции базы данных

Для управления схемой БД используется Alembic.

### Создание миграции
# Автоматическое создание миграции на основе изменений в моделях
uv run alembic revision --autogenerate -m "описание изменений"

# Пустая миграция для ручного заполнения
uv run alembic revision -m "описание изменений"

# Применить все миграции
uv run alembic upgrade head

# Применить следующую миграцию
uv run alembic upgrade +1

# Откатить последнюю миграцию
uv run alembic downgrade -1

# Откатить до конкретной версии
uv run alembic downgrade <revision_id>

# Откатить все миграции (очистить базу)
uv run alembic downgrade base