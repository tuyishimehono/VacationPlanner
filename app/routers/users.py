from fastapi import APIRouter

from app.dependencies import CurrentUser
from app.schemas.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
def read_me(user: CurrentUser):
    return user
