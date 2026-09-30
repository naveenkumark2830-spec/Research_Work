from enum import Enum
from typing import Optional
from pydantic import BaseModel


class VoiceStatus(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"


class VoiceState(BaseModel):
    status: VoiceStatus = VoiceStatus.IDLE
    current_speaker: Optional[str] = "Jarvis"
    is_listening: bool = False
    is_speaking: bool = False
    interruption_requested: bool = False
    last_transcript: Optional[str] = None
