import sqlite3
from collections.abc import Generator
from contextlib import contextmanager

from dive.schemas.base import EventModel

DB_PATH = "data/dive.db"


def connection(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            shipment_id TEXT PRIMARY KEY,
            schema_ver TEXT NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
          CREATE TABLE IF NOT EXISTS jobs (
          job_id TEXT PRIMARY KEY,
          cursor INTEGER NOT NULL
          )
         """
    )

    conn.execute(
        """
              CREATE TABLE IF NOT EXISTS dead_letters (
              job_id TEXT NOT NULL,
              raw TEXT NOT NULL,
              error TEXT NOT NULL
              )
             """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS job_files (
            job_id TEXT PRIMARY KEY,
            path TEXT NOT NULL
        )
        """
    )

    conn.execute(
            """
            CREATE TABLE IF NOT EXISTS batch_signatures (
                job_id TEXT NOT NULL,
                end_cursor INTEGER NOT NULL,
                signature TEXT NOT NULL,
                PRIMARY KEY (job_id, end_cursor) 
            )
            """
        )

    conn.commit()
    return conn


def save(connection: sqlite3.Connection, events: list[EventModel]) -> None:
    for event in events:
        connection.execute(
            "INSERT INTO records (shipment_id, schema_ver, payload) VALUES (?, ?, ?) "
            "ON CONFLICT(shipment_id) DO UPDATE SET "
            "schema_ver = excluded.schema_ver, payload = excluded.payload",
            (event.shipment_id, event.version, event.model_dump_json()),
        )


@contextmanager
def transaction(connection: sqlite3.Connection) -> Generator[None]:
    try:
        yield
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def set_cursor(connection: sqlite3.Connection, job_id: str, gruop_number: int) -> None:
    connection.execute(
        "INSERT INTO jobs (job_id, cursor) VALUES (?, ?) "
        "ON CONFLICT(job_id) DO UPDATE SET cursor = excluded.cursor",
        (job_id, gruop_number),
    )


def get_cursor(connection: sqlite3.Connection, job_id: str) -> int:
    item = connection.execute(
        "SELECT cursor FROM jobs WHERE job_id = ? ", (job_id,)
    ).fetchone()

    if item is None:
        return 0

    else:
        cursor: int = item[0]
        return cursor


def save_job_file(connection: sqlite3.Connection, job_id: str, path: str) -> None:
    connection.execute(
        "INSERT INTO job_files (job_id, path) VALUES (?, ?) "
        "ON CONFLICT(job_id) DO UPDATE SET path = excluded.path",
        (job_id, path),
    )


def get_job_file(connection: sqlite3.Connection, job_id: str) -> str | None:
    row = connection.execute(
        "SELECT path FROM job_files WHERE job_id = ?", (job_id,)
    ).fetchone()
    if row is None:
        return None
    path: str = row[0]
    return path


def count_dead_letters(connection: sqlite3.Connection, job_id: str) -> int:
    row = connection.execute(
        "SELECT COUNT(*) FROM dead_letters WHERE job_id = ?", (job_id,)
    ).fetchone()
    total: int = row[0]
    return total


def list_dead_letters(
    connection: sqlite3.Connection, job_id: str, limit: int, offset: int
) -> list[tuple[str, str]]:
    rows = connection.execute(
        "SELECT raw, error FROM dead_letters WHERE job_id = ? ORDER BY rowid LIMIT ? OFFSET ?",
        (job_id, limit, offset),
    ).fetchall()
    return [(str(raw), str(error)) for raw, error in rows]

def save_signature(connection: sqlite3.Connection, job_id: str, end_cursor: int, signature: str) -> None:
      connection.execute(
            "INSERT INTO batch_signatures (job_id, end_cursor, signature) VALUES (?, ?, ?) "
                    "ON CONFLICT(job_id, end_cursor) DO UPDATE SET signature = excluded.signature",
                    (job_id, end_cursor, signature),
        )
      