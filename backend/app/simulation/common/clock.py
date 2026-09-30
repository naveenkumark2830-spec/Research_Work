class SimulationClock:
    """Logical simulation clock for deterministic event ordering and timing."""

    def __init__(self, start_time: float = 0.0):
        self._current_time: float = start_time

    @property
    def current_time(self) -> float:
        return round(self._current_time, 3)

    def tick(self, duration: float = 1.0) -> float:
        """Advance simulation clock by duration ticks."""
        self._current_time += duration
        return self.current_time

    def reset(self, start_time: float = 0.0) -> None:
        self._current_time = start_time
