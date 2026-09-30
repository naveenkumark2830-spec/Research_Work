from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class LearningMode(str, Enum):
    LEARN = "LEARN"
    PRACTICE = "PRACTICE"
    QUIZ = "QUIZ"
    INTERVIEW = "INTERVIEW"
    CHALLENGE = "CHALLENGE"


class LearningState(BaseModel):
    current_mode: LearningMode = LearningMode.LEARN
    current_topic: str = "HDFS Architecture"
    questions_answered: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    mastery: float = 0.0
    weak_topics: List[str] = Field(default_factory=list)
    last_assessment_id: Optional[str] = None
