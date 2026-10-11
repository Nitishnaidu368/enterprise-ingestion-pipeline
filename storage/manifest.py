import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class Manifest:
    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS ingestions (
                source_path TEXT PRIMARY KEY,
                file_type TEXT NOT NULL,
                status TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                error TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        self.connection.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    def is_completed(self, source_path: str) -> bool:
        row = self.connection.execute(
            "SELECT status FROM ingestions WHERE source_path = ?",
            (source_path,),
        ).fetchone()
        return row is not None and row[0] == "completed"

    def mark_started(self, source_path: str, file_type: str) -> None:
        self.connection.execute("""
            INSERT INTO ingestions (source_path, file_type, status, chunk_count, error, updated_at)
            VALUES (?, ?, 'processing', 0, NULL, ?)
            ON CONFLICT(source_path) DO UPDATE SET
                file_type = excluded.file_type,
                status = 'processing',
                chunk_count = 0,
                error = NULL,
                updated_at = excluded.updated_at
        """, (source_path, file_type, self._now()))
        self.connection.commit()

    def mark_completed(self, source_path: str, chunk_count: int) -> None:
        self.connection.execute("""
            UPDATE ingestions
            SET status = 'completed', chunk_count = ?, error = NULL, updated_at = ?
            WHERE source_path = ?
        """, (chunk_count, self._now(), source_path))
        self.connection.commit()

    def mark_failed(self, source_path: str, file_type: str, error: str) -> None:
        self.connection.execute("""
            INSERT INTO ingestions (source_path, file_type, status, chunk_count, error, updated_at)
            VALUES (?, ?, 'failed', 0, ?, ?)
            ON CONFLICT(source_path) DO UPDATE SET
                file_type = excluded.file_type,
                status = 'failed',
                chunk_count = 0,
                error = excluded.error,
                updated_at = excluded.updated_at
        """, (source_path, file_type, error, self._now()))
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "Manifest":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

