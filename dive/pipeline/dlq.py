



from dataclasses import dataclass


@dataclass
class DeadLetter:
    raw: str
    error: str


class DeadLetterQueue:

    def __init__(self) -> None:
        self.dead_letters: list[DeadLetter] = []

    def add(self, raw: str, error: str) -> None:
        item = DeadLetter(raw=raw, error=error)

        self.dead_letters.append(item)
