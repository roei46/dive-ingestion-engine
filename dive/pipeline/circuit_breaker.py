import time
from collections.abc import Callable


class CircuitBreaker:
    def __init__(self, max_failures: int, cooldown: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.max_failures = max_failures
        self.cooldown = cooldown
        self.clock = clock
        self.state = "closed"
        self.failures = 0
        self.opened_at = 0.0


    def record_success(self) -> None:
        self.failures = 0
        self.state = "closed"

    def record_failure(self) -> None:
        self.failures += 1

        if self.failures >= self.max_failures:
            self.state = "open"
            self.opened_at = self.clock()

    def allow(self) -> bool:
        if self.state == "closed":
            return True

        if self.state == "open" and self.clock() - self.opened_at >= self.cooldown:
            self.state = "half_open"
            return True

        return False
