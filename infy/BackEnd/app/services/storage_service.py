import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteStorageService:
    def __init__(self):
        self._database_path = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "analyses.db"
        )
        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    analysis_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    language TEXT NOT NULL,
                    code TEXT NOT NULL,
                    syntax_valid INTEGER NOT NULL,
                    errors TEXT,
                    findings TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS remediations (
                    remediation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    finding_key TEXT NOT NULL,
                    remediation TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(analysis_id, finding_key)
                )
                """
            )

    @staticmethod
    def _decode(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "analysis_id": row["analysis_id"],
            "status": row["status"],
            "language": row["language"],
            "code": row["code"],
            "syntax_valid": bool(row["syntax_valid"]),
            "errors": json.loads(row["errors"]) if row["errors"] else None,
            "findings": json.loads(row["findings"])
            if row["findings"]
            else None,
            "created_at": row["created_at"],
        }

    def save_analysis(
        self,
        analysis_id: str,
        data: Dict[str, Any],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO analyses
                (
                    analysis_id,
                    status,
                    language,
                    code,
                    syntax_valid,
                    errors,
                    findings
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    data["status"],
                    data["language"],
                    data["code"],
                    int(data["syntax_valid"]),
                    json.dumps(data.get("errors")),
                    json.dumps(data.get("findings")),
                ),
            )

    def get_analysis(
        self,
        analysis_id: str,
    ) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM analyses WHERE analysis_id = ?",
                (analysis_id,),
            ).fetchone()

        return self._decode(row) if row else None

    def list_analyses(
        self,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM analyses
                ORDER BY created_at DESC, rowid DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [self._decode(row) for row in rows]

    def delete_analysis(
        self,
        analysis_id: str,
    ) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM analyses WHERE analysis_id = ?",
                (analysis_id,),
            )

        return cursor.rowcount > 0

    def save_remediation(
        self,
        analysis_id: str,
        finding_key: str,
        remediation: Dict[str, Any],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO remediations
                (
                    analysis_id,
                    finding_key,
                    remediation
                )
                VALUES (?, ?, ?)
                """,
                (
                    analysis_id,
                    finding_key,
                    json.dumps(remediation),
                ),
            )

    def get_remediations(
        self,
        analysis_id: str,
    ) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT finding_key, remediation
                FROM remediations
                WHERE analysis_id = ?
                ORDER BY remediation_id
                """,
                (analysis_id,),
            ).fetchall()

        return [
            {
                "finding_key": row["finding_key"],
                "remediation": json.loads(row["remediation"]),
            }
            for row in rows
        ]

    def generate_id(self) -> str:
        # Generates a unique 8-character ID for analysis
        return uuid.uuid4().hex[:8]


storage_service = SQLiteStorageService()