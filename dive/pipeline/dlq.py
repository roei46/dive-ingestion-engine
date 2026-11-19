import sqlite3
from dataclasses import dataclass


@dataclass
class DeadLetter:
    raw: str
    error: str


class DeadLetterQueue:
    def __init__(self, connection: sqlite3.Connection, job_id: str) -> None:
        self.count = 0
        self.conn = connection
        self.job_id = job_id

    def add(self, raw: str, error: str) -> None:
        self.conn.execute(
            "INSERT INTO dead_letters (job_id, raw, error) VALUES (?, ?, ?) ",
            (self.job_id, raw, error),
        )

        self.count += 1
