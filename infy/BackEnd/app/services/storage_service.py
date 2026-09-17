import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_FILENAMES = {
    "python": "main.py",
    "java": "Main.java",
    "javascript": "app.js",
    "typescript": "app.ts",
    "cpp": "main.cpp",
    "go": "main.go",
    "html": "index.html",
}


def get_default_filename(language: str) -> str:
    lang = (language or "python").lower()
    return DEFAULT_FILENAMES.get(lang, f"main.{lang}")


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
                    filename TEXT,
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

            # Auto-migrate table if filename or user_id columns don't exist yet
            try:
                connection.execute("ALTER TABLE analyses ADD COLUMN filename TEXT")
            except sqlite3.OperationalError:
                pass
            try:
                connection.execute("ALTER TABLE analyses ADD COLUMN user_id TEXT")
            except sqlite3.OperationalError:
                pass

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

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'developer',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Seed default Admin and Developer accounts if missing
            self._seed_default_users(connection)

    def _seed_default_users(self, connection: sqlite3.Connection):
        from app.core.security import hash_password

        # Admin user
        admin_email = "admin@codeguard.ai"
        cursor = connection.execute("SELECT user_id FROM users WHERE email = ?", (admin_email,))
        if not cursor.fetchone():
            connection.execute(
                "INSERT INTO users (user_id, email, hashed_password, full_name, role, is_active) VALUES (?, ?, ?, ?, ?, ?)",
                ("usr_admin01", admin_email, hash_password("admin"), "System Admin", "admin", 1)
            )

        # Developer user
        dev_email = "sumit@codeguard.ai"
        cursor = connection.execute("SELECT user_id FROM users WHERE email = ?", (dev_email,))
        if not cursor.fetchone():
            connection.execute(
                "INSERT INTO users (user_id, email, hashed_password, full_name, role, is_active) VALUES (?, ?, ?, ?, ?, ?)",
                ("usr_dev01", dev_email, hash_password("password123"), "Sumit Kumar Singh", "developer", 1)
            )

    @staticmethod
    def _decode(row: sqlite3.Row) -> Dict[str, Any]:
        keys = row.keys()
        return {
            "analysis_id": row["analysis_id"],
            "filename": row["filename"] if "filename" in keys and row["filename"] else get_default_filename(row["language"]),
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
        filename = data.get("filename") or get_default_filename(data.get("language"))
        user_id = data.get("user_id")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO analyses
                (
                    analysis_id,
                    filename,
                    user_id,
                    status,
                    language,
                    code,
                    syntax_valid,
                    errors,
                    findings
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    filename,
                    user_id,
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
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            if user_id:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM analyses
                    WHERE user_id = ?
                    ORDER BY created_at DESC, rowid DESC
                    LIMIT ?
                    """,
                    (user_id, limit),
                ).fetchall()
            else:
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

    # ============================================================
    # USER & AUTHENTICATION METHODS
    # ============================================================

    def create_user(self, email: str, hashed_password: str, full_name: str, role: str = "developer") -> Dict[str, Any]:
        user_id = f"usr_{uuid.uuid4().hex[:8]}"
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (user_id, email, hashed_password, full_name, role, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (user_id, email.lower().strip(), hashed_password, full_name.strip(), role),
            )
        return self.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.lower().strip(),)
            ).fetchone()
            if not row:
                return None
            return dict(row)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            if not row:
                return None
            return dict(row)

    def list_users(self) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT user_id, email, full_name, role, is_active, created_at FROM users ORDER BY created_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def toggle_user_status(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        val = user.get("is_active")
        is_active = bool(val)
        new_status = 0 if is_active else 1
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE users SET is_active = ? WHERE user_id = ?",
                (new_status, user_id)
            )
            return cursor.rowcount > 0

    def get_admin_stats(self) -> Dict[str, Any]:
        analyses = self.list_analyses()
        users = self.list_users()

        total_users = len(users)
        active_users = sum(1 for u in users if u.get("is_active") == 1)
        total_analyses = len(analyses)

        total_findings = 0
        high_findings = 0
        medium_findings = 0
        low_findings = 0

        sqli_count = 0
        secret_count = 0
        command_inj_count = 0
        xss_count = 0
        smell_count = 0

        scores = []

        for item in analyses:
            findings = item.get("findings") or []
            item_high = 0
            item_medium = 0
            item_low = 0

            for f in findings:
                if f.get("title") == "Software Architecture Metrics":
                    continue
                sev = str(f.get("severity") or "").lower()
                title = str(f.get("title") or "")
                total_findings += 1

                if sev == "high":
                    high_findings += 1
                    item_high += 1
                elif sev == "medium":
                    medium_findings += 1
                    item_medium += 1
                else:
                    low_findings += 1
                    item_low += 1

                if "SQL Injection" in title:
                    sqli_count += 1
                elif "Secret" in title or "Credential" in title:
                    secret_count += 1
                elif "Command Injection" in title:
                    command_inj_count += 1
                elif "XSS" in title:
                    xss_count += 1
                else:
                    smell_count += 1

            item_score = max(0, min(100, 100 - item_high * 15 - item_medium * 8 - item_low * 3))
            scores.append(item_score)

        avg_health_score = round(sum(scores) / len(scores), 1) if scores else 100.0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_analyses": total_analyses,
            "total_findings": total_findings,
            "severity_breakdown": {
                "high": high_findings,
                "medium": medium_findings,
                "low": low_findings
            },
            "threat_distribution": {
                "sql_injection": sqli_count,
                "hardcoded_secrets": secret_count,
                "command_injection": command_inj_count,
                "xss": xss_count,
                "code_smells": smell_count
            },
            "average_health_score": avg_health_score,
            "recent_audit_logs": [
                {
                    "analysis_id": item["analysis_id"],
                    "filename": item.get("filename"),
                    "language": item.get("language"),
                    "findings_count": len(item.get("findings") or []),
                    "created_at": item.get("created_at")
                }
                for item in analyses[:10]
            ]
        }


try:
    from app.services.mongodb_storage_service import MongoDBStorageService
    storage_service = MongoDBStorageService()
    print("[INIT] Connected to MongoDB Atlas Cloud Database successfully.")
except Exception as _err:
    print(f"[INIT] MongoDB Atlas fallback to SQLite Storage: {_err}")
    storage_service = SQLiteStorageService()