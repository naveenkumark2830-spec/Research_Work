import uuid
from typing import Optional, List, Dict, Any
from app.models.user import User
from app.core.exceptions import ResourceNotFoundError
from app.repositories.user_repository import IUserRepository


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def create_user(self, display_name: str, preferences: Optional[Dict[str, Any]] = None) -> User:
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        user = User(
            user_id=user_id,
            display_name=display_name,
            preferences=preferences or {}
        )
        return self.user_repo.create(user)

    def get_user(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User", user_id)
        return user

    def list_users(self) -> List[User]:
        return self.user_repo.list_all()
