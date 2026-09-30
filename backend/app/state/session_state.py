from pydantic import BaseModel, Field
from app.models.user import User
from app.models.session import Session
from app.models.conversation import ConversationState
from app.models.simulation import SimulationState
from app.models.visualization import VisualizationState
from app.models.voice import VoiceState
from app.models.learning import LearningState


class SessionState(BaseModel):
    user: User
    session: Session
    conversation: ConversationState = Field(default_factory=ConversationState)
    simulation: SimulationState = Field(default_factory=SimulationState)
    visualization: VisualizationState = Field(default_factory=VisualizationState)
    voice: VoiceState = Field(default_factory=VoiceState)
    learning: LearningState = Field(default_factory=LearningState)
    state_version: int = 1
