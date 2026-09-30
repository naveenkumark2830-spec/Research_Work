import pytest

from app.jarvis.schemas import SimulationAction
from app.jarvis.action_validator import (
    ActionValidationError,
    bytes_from_size,
    validate_simulation_action,
)


def test_gigabyte_conversion():
    assert bytes_from_size(1, "GB") == 1024 ** 3


def test_megabyte_conversion():
    assert bytes_from_size(128, "MB") == 128 * 1024 ** 2


def test_write_file_size_validation():
    action = SimulationAction(
        action="write_file",
        parameters={
            "path": "/teddy/demo-file",
            "size": 1,
            "unit": "GB",
        },
    )

    validated = validate_simulation_action(action)

    assert validated.parameters["size_bytes"] == 1024 ** 3


def test_invalid_zero_size():
    with pytest.raises((ValueError, ActionValidationError, Exception)):
        action = SimulationAction(
            action="write_file",
            parameters={
                "path": "/teddy/demo-file",
                "size_bytes": 0,
            },
        )
        validate_simulation_action(action)


def test_invalid_unit():
    with pytest.raises(ActionValidationError):
        bytes_from_size(1, "INVALID")
