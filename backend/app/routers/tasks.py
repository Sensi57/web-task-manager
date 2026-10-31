from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

# Все endpoints этого роутера защищены JWT-токеном
router = APIRouter(prefix="/tasks", tags=["Tasks"], dependencies=[Depends(get_current_user)])


def _get_own_task(task_id: int, user: models.User, db: Session) -> models.Task:
    task = db.get(models.Task, task_id)
    # Чужую задачу не раскрываем — отвечаем 404, как будто её нет
    if task is None or task.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return task


@router.get("", response_model=list[schemas.TaskOut], summary="Список задач текущего пользователя")
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    done: bool | None = None,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(models.Task).where(models.Task.owner_id == user.id)
    if done is not None:
        query = query.where(models.Task.done == done)
    return db.scalars(query.order_by(models.Task.id).offset(skip).limit(limit)).all()


@router.get("/{task_id}", response_model=schemas.TaskOut, summary="Получить задачу по ID")
def get_task(task_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_own_task(task_id, user, db)


@router.post("", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED, summary="Создать задачу")
def create_task(
    data: schemas.TaskCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = models.Task(**data.model_dump(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=schemas.TaskOut, summary="Обновить задачу")
def update_task(
    task_id: int,
    data: schemas.TaskUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = _get_own_task(task_id, user, db)
    for field, value in data.model_dump().items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить задачу")
def delete_task(task_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = _get_own_task(task_id, user, db)
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
