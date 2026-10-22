from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import db
from app.schemas.user import Token, User, UserCreate, UserInDB
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

def _find_user_by_email(email: str) -> UserInDB | None:
    return next((u for u in db.users.values() if u.email == email.lower()), None)

@router.post("/register", response_model=User, status_code=201)
def register(data: UserCreate):
    if _find_user_by_email(data.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = UserInDB(
        id=next(db.user_ids),
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
    )
    db.users[user.id] = user
    return user

@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = _find_user_by_email(form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))
