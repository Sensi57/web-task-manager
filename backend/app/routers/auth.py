from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.User).where(models.User.username == data.username)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")

    user = models.User(username=data.username, hashed_password=security.hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=schemas.Token,
    summary="Логин: получить JWT-токен",
    description="Принимает form-data (`username`, `password`). Именно этот endpoint использует кнопка **Authorize** в Swagger.",
)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.username == form.username))
    if user is None or not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=security.create_access_token(user.username))


@router.get("/me", response_model=schemas.UserOut, summary="Текущий пользователь (по токену)")
def me(current_user: models.User = Depends(security.get_current_user)):
    return current_user
