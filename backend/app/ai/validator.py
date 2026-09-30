from __future__ import annotations

from typing import Any
from .action import Action, ActionType, IntentResult
from .exceptions import InvalidAIActionError
from .intent import IntentType


class AIActionValidator:

    MIN_CONFIDENCE = 0.70

    def validate(
        self,
        result: IntentResult,
    ) -> IntentResult:

        if result.confidence < self.MIN_CONFIDENCE:
            raise InvalidAIActionError(
                "Teddy is not confident enough to perform this action."
            )

        if result.intent == IntentType.CREATE_HDFS_FILE:
            self._validate_create_file(result)

        elif result.intent == IntentType.SIMULATE_FAILURE:
            self._validate_failure(result)

        return result

    @staticmethod
    def _validate_create_file(
        result: IntentResult,
    ):

        params = result.parameters

        required = [
            "file_size_mb",
            "block_size_mb",
            "replication_factor",
        ]

        missing = [
            key
            for key in required
            if key not in params
        ]

        if missing:
            raise InvalidAIActionError(
                f"Missing parameters: {missing}"
            )

        file_size = params["file_size_mb"]
        block_size = params["block_size_mb"]
        replication = params["replication_factor"]

        if file_size <= 0:
            raise InvalidAIActionError(
                "File size must be greater than zero."
            )

        if block_size <= 0:
            raise InvalidAIActionError(
                "Block size must be greater than zero."
            )

        if replication < 1:
            raise InvalidAIActionError(
                "Replication factor must be at least 1."
            )

    @staticmethod
    def _validate_failure(
        result: IntentResult,
    ):

        params = result.parameters

        if not params.get("node_id"):
            raise InvalidAIActionError(
                "DataNode identifier is required."
            )


class ActionValidator:
    """Validator for Level 7 Orchestrator Actions."""

    ALLOWED_CONFIG_KEYS = {
        "file_size_mb", "file_size", "block_size_mb", "block_size",
        "replication_factor", "datanode_count", "reducer_count",
        "custom_parameters", "simulation_speed"
    }

    @staticmethod
    def validate_action(action: Any, state: Any = None) -> Any:
        if action is None:
            return action

        if isinstance(action, Action):
            if action.type == ActionType.SET_SPEED:
                speed = (action.parameters or {}).get("speed", 1.0)
                if speed <= 0 or speed > 20:
                    raise InvalidAIActionError("Speed must be between 0.1x and 20x.")

            if action.type == ActionType.UPDATE_CONFIG:
                params = action.parameters or {}
                for key, val in params.items():
                    if key not in ActionValidator.ALLOWED_CONFIG_KEYS or "eval" in key or "exec" in key or "import" in str(val).lower() or "os." in str(val).lower():
                        raise InvalidAIActionError(f"Invalid configuration parameter: {key}")

        elif hasattr(action, "confidence"):
            if getattr(action, "confidence", 1.0) < 0.5:
                raise InvalidAIActionError("AI confidence score is too low.")
        elif isinstance(action, dict):
            if action.get("confidence", 1.0) < 0.5:
                raise InvalidAIActionError("AI confidence score is too low.")

        return action
