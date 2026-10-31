import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from . import models  # noqa: F401  (регистрирует модели в Base.metadata)
from .database import Base, engine
from .routers import auth, tasks


def init_db(retries: int = 15, delay: float = 2.0) -> None:
    """Создаёт таблицы. Повторяет попытки, пока PostgreSQL не станет доступен."""
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            print(f"Database not ready (attempt {attempt}/{retries}), retrying in {delay}s...")
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description=(
        "REST API для управления задачами с JWT-авторизацией.\n\n"
        "**Как авторизоваться в Swagger:** зарегистрируйтесь через `POST /auth/register`, "
        "затем нажмите кнопку **Authorize** и введите username/password."
    ),
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["Health"], summary="Проверка работоспособности")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
