from abc import ABC, abstractmethod
import json
from typing import Optional, List
from sqlalchemy.orm import Session as DBSession
from app.models.user import User
from app.db.models import UserModel


class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        pass


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db: DBSession):
        self.db = db

    def create(self, user: User) -> User:
        db_user = UserModel(
            user_id=user.user_id,
            display_name=user.display_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            preferences_json=json.dumps(user.preferences)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if not db_user:
            return None
        return User(
            user_id=db_user.user_id,
            display_name=db_user.display_name,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            preferences=json.loads(db_user.preferences_json or "{}")
        )

    def list_all(self) -> List[User]:
        db_users = self.db.query(UserModel).all()
        return [
            User(
                user_id=u.user_id,
                display_name=u.display_name,
                created_at=u.created_at,
                updated_at=u.updated_at,
                preferences=json.loads(u.preferences_json or "{}")
            )
            for u in db_users
        ]
