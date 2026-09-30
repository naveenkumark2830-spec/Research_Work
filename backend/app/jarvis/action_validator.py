from __future__ import annotations

from typing import Any

from .schemas import SimulationAction


UNIT_MULTIPLIERS = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 ** 2,
    "GB": 1024 ** 3,
    "TB": 1024 ** 4,
}


class ActionValidationError(ValueError):
    """Raised when Teddy proposes an invalid simulation action."""


def bytes_from_size(value: Any, unit: str | None = None) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ActionValidationError(
            f"Invalid size value: {value}"
        ) from exc

    normalized_unit = (unit or "B").upper()

    if normalized_unit not in UNIT_MULTIPLIERS:
        raise ActionValidationError(
            f"Unsupported size unit: {normalized_unit}"
        )

    result = number * UNIT_MULTIPLIERS[normalized_unit]

    if result <= 0:
        raise ActionValidationError(
            "Size must be greater than zero"
        )

    return int(result)


def validate_simulation_action(
    action: SimulationAction,
) -> SimulationAction:

    if action.action != "write_file":
        return action

    params = dict(action.parameters)

    # --------------------------------------------------
    # FILE SIZE
    # --------------------------------------------------

    if "size_bytes" in params:
        size_bytes = params["size_bytes"]

        if not isinstance(size_bytes, int):
            raise ActionValidationError(
                "size_bytes must be an integer"
            )

        if size_bytes <= 0:
            raise ActionValidationError(
                "size_bytes must be greater than zero"
            )

    elif "size" in params:
        size_bytes = bytes_from_size(
            params["size"],
            params.get("unit"),
        )

        params["size_bytes"] = size_bytes

    else:
        raise ActionValidationError(
            "write_file requires size_bytes or size + unit"
        )

    # --------------------------------------------------
    # PATH
    # --------------------------------------------------

    path = params.get("path", "/teddy/demo-file")

    if not isinstance(path, str) or not path.startswith("/"):
        raise ActionValidationError(
            "HDFS path must start with '/'"
        )

    params["path"] = path

    # --------------------------------------------------
    # BLOCK SIZE
    # --------------------------------------------------

    if "block_size_bytes" in params:
        block_size_bytes = params["block_size_bytes"]

    elif "block_size" in params:
        block_size_bytes = bytes_from_size(
            params["block_size"],
            params.get("block_unit", "MB"),
        )

    else:
        block_size_bytes = 128 * 1024 ** 2

    if not isinstance(block_size_bytes, int):
        raise ActionValidationError(
            "block_size_bytes must be an integer"
        )

    if block_size_bytes <= 0:
        raise ActionValidationError(
            "block_size_bytes must be greater than zero"
        )

    params["block_size_bytes"] = block_size_bytes

    # --------------------------------------------------
    # REPLICATION
    # --------------------------------------------------

    replication_factor = params.get(
        "replication_factor",
        3,
    )

    if not isinstance(replication_factor, int):
        raise ActionValidationError(
            "replication_factor must be an integer"
        )

    if replication_factor < 1:
        raise ActionValidationError(
            "replication_factor must be at least 1"
        )

    params["replication_factor"] = replication_factor

    return SimulationAction(
        action=action.action,
        parameters=params,
    )
