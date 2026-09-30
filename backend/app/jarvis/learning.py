import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class LearningManager:
    """
    Manages quiz questions and misconception detection using local datasets.
    """

    def __init__(self, data_dir: Optional[str] = None):
        base_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent.parent.parent / "data"
        self.misconceptions_path = base_dir / "misconceptions.json"
        self.quiz_path = base_dir / "quiz_questions.json"

        self.misconceptions: List[Dict[str, Any]] = []
        self.quiz_questions: List[Dict[str, Any]] = []

        self.load_data()

    def load_data(self):
        if self.misconceptions_path.exists():
            try:
                with open(self.misconceptions_path, "r", encoding="utf-8") as f:
                    self.misconceptions = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load misconceptions.json: {e}")

        if self.quiz_path.exists():
            try:
                with open(self.quiz_path, "r", encoding="utf-8") as f:
                    self.quiz_questions = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load quiz_questions.json: {e}")

    def check_misconception(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Check if user input exhibits a known Hadoop misconception.
        """
        t = text.lower()
        for mc in self.misconceptions:
            statement = mc.get("student_statement", "").lower()
            # Simple keyword / semantic similarity check
            keywords = [w for w in statement.split() if len(w) > 3 and w not in ["the", "that", "this", "with", "from"]]
            matches = sum(1 for kw in keywords if kw in t)
            if matches >= min(3, len(keywords)):
                return mc
        return None

    def get_quiz_question(self, topic: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a quiz question, optionally filtered by topic.
        """
        if not self.quiz_questions:
            return None

        if topic:
            filtered = [q for q in self.quiz_questions if q.get("topic", "").lower() == topic.lower()]
            if filtered:
                return filtered[0]

        return self.quiz_questions[0]
