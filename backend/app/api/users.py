from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import CreateUserRequest, UserResponse
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(db: DBSession = Depends(get_db)) -> UserService:
    repo = SQLAlchemyUserRepository(db)
    return UserService(repo)


@router.post("", response_model=UserResponse, status_code=201, summary="Create User")
def create_user(
    request: CreateUserRequest,
    service: UserService = Depends(get_user_service)
):
    user = service.create_user(
        display_name=request.display_name,
        preferences=request.preferences
    )
    return UserResponse(user=user)


@router.get("/{user_id}", response_model=UserResponse, summary="Get User Details")
def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    user = service.get_user(user_id)
    return UserResponse(user=user)
