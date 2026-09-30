import uuid
from datetime import datetime, timezone
from typing import Optional
from app.models.conversation import Message, MessageRole
from app.models.event import Event, EventType
from app.state.session_state import SessionState
from app.core.exceptions import ResourceNotFoundError, UserIsolationError
from app.repositories.session_repository import ISessionRepository
from app.repositories.conversation_repository import IConversationRepository
from app.repositories.event_repository import IEventRepository


class ConversationService:
    def __init__(
        self,
        session_repo: ISessionRepository,
        conversation_repo: IConversationRepository,
        event_repo: IEventRepository
    ):
        self.session_repo = session_repo
        self.conversation_repo = conversation_repo
        self.event_repo = event_repo

    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        now = datetime.now(timezone.utc)
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        message = Message(
            message_id=message_id,
            role=role,
            content=content,
            timestamp=now
        )

        # Update ConversationState
        state.conversation.recent_messages.append(message)
        state.conversation.conversation_turn_count += 1
        if role == MessageRole.USER:
            state.conversation.last_user_message = content
        elif role == MessageRole.ASSISTANT:
            state.conversation.last_assistant_message = content

        state.session.updated_at = now
        state.session.last_activity_at = now
        state.state_version += 1

        # Save to repositories
        self.conversation_repo.save_message(session_id, message)
        self.session_repo.save_state(state)

        # Log event
        seq_num = self.event_repo.get_next_sequence_number(session_id)
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            event_type=EventType.CONVERSATION_MESSAGE_ADDED,
            timestamp=now,
            sequence_number=seq_num,
            payload={"message_id": message_id, "role": role.value, "content": content},
            state_version=state.state_version
        )
        self.event_repo.save(event)

        return state
