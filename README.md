# Task Manager API

Контейнеризированное REST API: **FastAPI** (backend) + **PostgreSQL** (база данных) + **Docker Compose**.
Авторизация через **JWT-токены**, документация через **Swagger UI**.

## Архитектура

```
 Postman / Swagger UI
        │  http://localhost:8000
        ▼
┌─────────────────┐    app-net (bridge)    ┌──────────────────┐
│ backend (FastAPI)│ ─────────────────────▶ │ db (PostgreSQL)  │
│  порт 8000       │   postgres://db:5432   │  порт 5432       │
└─────────────────┘                        └────────┬─────────┘
                                                    │
                                           именованный том pgdata
```

- **backend** собирается из собственного `backend/Dockerfile`.
- **db** — образ `postgres:16-alpine`, данные лежат в именованном томе `pgdata`.
- Сервисы общаются по пользовательской сети `app-net`; backend обращается к БД по имени сервиса `db`.
- Порт БД наружу не публикуется — доступна только backend'у.
- backend стартует после того, как healthcheck БД (`pg_isready`) станет «healthy».
- Вся конфигурация — через переменные окружения из `.env`.

## Быстрый старт

```bash
cp .env.example .env      # если .env ещё нет; при желании поменять значения
docker compose up --build
```

После запуска:

| Что | Адрес |
|-----|-------|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health | http://localhost:8000/health |

Остановка: `docker compose down` (данные сохраняются).
Полная очистка вместе с данными: `docker compose down -v`.

## Переменные окружения (`.env`)

| Переменная | Описание | Пример |
|------------|----------|--------|
| `POSTGRES_USER` | Пользователь БД | `taskuser` |
| `POSTGRES_PASSWORD` | Пароль БД | `taskpass123` |
| `POSTGRES_DB` | Имя БД | `taskdb` |
| `SECRET_KEY` | Секрет для подписи JWT (`openssl rand -hex 32`) | — |
| `JWT_ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `60` |
| `BACKEND_PORT` | Порт backend на хосте | `8000` |

`.env` не коммитится в git (см. `.gitignore`); шаблон — `.env.example`. Рабочий `.env` сдаётся отдельным zip-архивом.

## Авторизация и Swagger

1. Открыть http://localhost:8000/docs
2. `POST /auth/register` → создать пользователя.
3. Нажать **Authorize** → ввести `username` и `password` → **Authorize**.
4. Теперь защищённые endpoints (`/tasks`, `/auth/me`) доступны прямо из Swagger.

## Postman

Файл: `postman/TaskManager.postman_collection.json` → Postman → **Import**.

Запускать по порядку сверху вниз (или Collection Runner): **Register → Login** (токен сохраняется в переменную `token` автоматически) → остальные запросы. В запросах `Create task` сохраняется `taskId`, который используют Get / Update / Delete. В каждом запросе есть тесты.

## API

Полное описание всех endpoints: [docs/API.md](docs/API.md).

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Получить JWT |
| GET | `/auth/me` | Текущий пользователь |
| GET | `/tasks` | Список задач |
| GET | `/tasks/{id}` | Задача по ID |
| POST | `/tasks` | Создать |
| PUT | `/tasks/{id}` | Обновить |
| DELETE | `/tasks/{id}` | Удалить |

## Структура репозитория

```
.
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # приложение FastAPI, инициализация БД
│       ├── database.py      # подключение SQLAlchemy
│       ├── models.py        # таблицы users, tasks
│       ├── schemas.py       # Pydantic-схемы
│       ├── security.py      # хеширование паролей, JWT
│       └── routers/
│           ├── auth.py      # /auth/*
│           └── tasks.py     # /tasks/*
├── docs/API.md
├── postman/TaskManager.postman_collection.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Проверка персистентности данных

```bash
docker compose down        # контейнеры удалены, том остался
docker compose up          # пользователи и задачи на месте
docker volume ls           # виден том <папка>_pgdata
```
