from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session as DBSession
from app.models.conversation import Message, MessageRole
from app.db.models import MessageModel


class IConversationRepository(ABC):
    @abstractmethod
    def save_message(self, session_id: str, message: Message) -> Message:
        pass

    @abstractmethod
    def get_messages(self, session_id: str) -> List[Message]:
        pass


class SQLAlchemyConversationRepository(IConversationRepository):
    def __init__(self, db: DBSession):
        self.db = db

    def save_message(self, session_id: str, message: Message) -> Message:
        db_message = MessageModel(
            message_id=message.message_id,
            session_id=session_id,
            role=message.role.value,
            content=message.content,
            timestamp=message.timestamp
        )
        self.db.add(db_message)
        self.db.commit()
        return message

    def get_messages(self, session_id: str) -> List[Message]:
        db_messages = (
            self.db.query(MessageModel)
            .filter(MessageModel.session_id == session_id)
            .order_by(MessageModel.timestamp.asc())
            .all()
        )
        return [
            Message(
                message_id=m.message_id,
                role=MessageRole(m.role),
                content=m.content,
                timestamp=m.timestamp
            )
            for m in db_messages
        ]
