# API Documentation — Task Manager API

Base URL: `http://localhost:8000`

Интерактивная документация (Swagger UI): **http://localhost:8000/docs**
ReDoc: http://localhost:8000/redoc · OpenAPI JSON: http://localhost:8000/openapi.json

## Авторизация

API использует **JWT Bearer-токены**.

1. `POST /auth/register` — создать пользователя.
2. `POST /auth/login` — получить `access_token`.
3. Передавать токен в заголовке `Authorization: Bearer <access_token>`.

Все endpoints `/tasks*` и `/auth/me` требуют токен. Без токена или с невалидным/просроченным токеном — `401 Unauthorized`.
Каждый пользователь видит и изменяет **только свои** задачи.

В Swagger UI: кнопка **Authorize** → ввести `username` и `password` → токен подставится автоматически.

## Endpoints

| Метод | Путь | Авторизация | Описание | Успех |
|-------|------|:-----------:|----------|-------|
| GET | `/health` | — | Проверка сервиса и БД | 200 |
| POST | `/auth/register` | — | Регистрация | 201 |
| POST | `/auth/login` | — | Логин, получение JWT | 200 |
| GET | `/auth/me` | ✅ | Текущий пользователь | 200 |
| GET | `/tasks` | ✅ | Список задач (**list**) | 200 |
| GET | `/tasks/{id}` | ✅ | Задача по ID (**get by ID**) | 200 |
| POST | `/tasks` | ✅ | Создать задачу (**create**) | 201 |
| PUT | `/tasks/{id}` | ✅ | Обновить задачу (**update**) | 200 |
| DELETE | `/tasks/{id}` | ✅ | Удалить задачу (**delete**) | 204 |

---

### POST `/auth/register`
Body (JSON):
```json
{ "username": "alex", "password": "secret123" }
```
Ограничения: username 3–50 символов, password 6–72 символа.

Ответы: `201` — `{ "id": 1, "username": "alex", "created_at": "..." }` · `409` — имя занято · `422` — ошибка валидации.

### POST `/auth/login`
Body: `application/x-www-form-urlencoded` — поля `username`, `password`.

Ответы: `200` — `{ "access_token": "<jwt>", "token_type": "bearer" }` · `401` — неверный логин/пароль.

### GET `/auth/me`
Ответы: `200` — данные пользователя · `401` — нет/неверный токен.

### GET `/tasks`
Query-параметры: `skip` (по умолчанию 0), `limit` (по умолчанию 100), `done` (`true`/`false`, необязательно).

Ответ `200`:
```json
[
  {
    "id": 1,
    "title": "Сдать проект по Docker",
    "description": "Подготовить Postman и README",
    "done": false,
    "owner_id": 1,
    "created_at": "2026-10-31T07:00:00Z"
  }
]
```

### GET `/tasks/{id}`
Ответы: `200` — задача · `404` — не найдена (или принадлежит другому пользователю) · `401`.

### POST `/tasks`
Body (JSON):
```json
{ "title": "Сдать проект по Docker", "description": "Подготовить Postman и README", "done": false }
```
`title` обязателен (1–200 символов), `description` и `done` необязательны.

Ответы: `201` — созданная задача · `422` · `401`.

### PUT `/tasks/{id}`
Body — те же поля, что при создании (полная замена). Ответы: `200` · `404` · `422` · `401`.

### DELETE `/tasks/{id}`
Ответы: `204` (пустое тело) · `404` · `401`.

## Коды ошибок

| Код | Значение |
|-----|----------|
| 401 | Нет токена, токен невалиден или просрочен / неверный логин |
| 404 | Ресурс не найден |
| 409 | Имя пользователя уже занято |
| 422 | Некорректные данные в запросе |
