import json
import uuid
import datetime
from typing import Any, Dict, List, Optional
from pymongo import MongoClient, DESCENDING

from app.core.security import hash_password

MONGODB_URI = "mongodb+srv://cricketinfo243_db_user:YlIhnEouxCENqi3K@smartcodeinspection.ku3jwwj.mongodb.net/smartcodeinspection?retryWrites=true&w=majority"


class MongoDBStorageService:
    def __init__(self, uri: str = MONGODB_URI):
        self.uri = uri
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client["smartcodeinspection"]
        self.analyses = self.db["analyses"]
        self.remediations = self.db["remediations"]
        self.users = self.db["users"]

        self._initialize_indexes()
        self._seed_default_users()

    def _initialize_indexes(self):
        try:
            self.analyses.create_index("analysis_id", unique=True)
            self.users.create_index("email", unique=True)
            self.users.create_index("user_id", unique=True)
            self.remediations.create_index([("analysis_id", 1), ("finding_key", 1)], unique=True)
        except Exception:
            pass

    def _seed_default_users(self):
        try:
            # Seed Admin
            if not self.users.find_one({"email": "admin@codeguard.ai"}):
                self.users.insert_one({
                    "user_id": "usr_admin01",
                    "email": "admin@codeguard.ai",
                    "hashed_password": hash_password("admin"),
                    "full_name": "System Admin",
                    "role": "admin",
                    "is_active": True,
                    "created_at": datetime.datetime.utcnow().isoformat()
                })

            # Seed Developer
            if not self.users.find_one({"email": "sumit@codeguard.ai"}):
                self.users.insert_one({
                    "user_id": "usr_dev01",
                    "email": "sumit@codeguard.ai",
                    "hashed_password": hash_password("password123"),
                    "full_name": "Sumit Kumar Singh",
                    "role": "developer",
                    "is_active": True,
                    "created_at": datetime.datetime.utcnow().isoformat()
                })
        except Exception:
            pass

    # ============================================================
    # CODE ANALYSIS METHODS
    # ============================================================

    def save_analysis(
        self,
        analysis_id: str,
        data_or_filename: Any = None,
        status: Optional[str] = None,
        language: Optional[str] = None,
        code: Optional[str] = None,
        syntax_valid: Optional[bool] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        findings: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if isinstance(data_or_filename, dict):
            data = data_or_filename
            filename = data.get("filename") or ("main." + ("py" if data.get("language") == "python" else "java"))
            status = data.get("status", "completed")
            language = data.get("language", "python")
            code = data.get("code", "")
            syntax_valid = data.get("syntax_valid", True)
            errors = data.get("errors") or []
            findings = data.get("findings") or []
        else:
            filename = data_or_filename or ("main." + ("py" if (language or "python") == "python" else "java"))

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        doc = {
            "analysis_id": analysis_id,
            "filename": filename,
            "status": status,
            "language": language,
            "code": code,
            "syntax_valid": bool(syntax_valid),
            "errors": errors or [],
            "findings": findings or [],
            "created_at": now_str,
        }

        self.analyses.replace_one({"analysis_id": analysis_id}, doc, upsert=True)

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        doc = self.analyses.find_one({"analysis_id": analysis_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return doc

    def list_analyses(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.analyses.find().sort("created_at", DESCENDING).limit(limit)
        results = []
        for doc in cursor:
            doc.pop("_id", None)
            results.append(doc)
        return results

    def delete_analysis(self, analysis_id: str) -> bool:
        res = self.analyses.delete_one({"analysis_id": analysis_id})
        self.remediations.delete_many({"analysis_id": analysis_id})
        return res.deleted_count > 0

    # ============================================================
    # REMEDIATION METHODS
    # ============================================================

    def save_remediation(
        self,
        analysis_id: str,
        finding_key: str,
        remediation: Dict[str, Any],
    ) -> None:
        doc = {
            "analysis_id": analysis_id,
            "finding_key": finding_key,
            "remediation": remediation,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        self.remediations.replace_one(
            {"analysis_id": analysis_id, "finding_key": finding_key},
            doc,
            upsert=True
        )

    def get_remediations(
        self,
        analysis_id: str,
    ) -> List[Dict[str, Any]]:
        cursor = self.remediations.find({"analysis_id": analysis_id})
        results = []
        for doc in cursor:
            results.append({
                "finding_key": doc["finding_key"],
                "remediation": doc["remediation"]
            })
        return results

    # ============================================================
    # USER & AUTHENTICATION METHODS
    # ============================================================

    def create_user(self, email: str, hashed_password: str, full_name: str, role: str = "developer") -> Dict[str, Any]:
        user_id = f"usr_{uuid.uuid4().hex[:8]}"
        doc = {
            "user_id": user_id,
            "email": email.lower().strip(),
            "hashed_password": hashed_password,
            "full_name": full_name.strip(),
            "role": role,
            "is_active": True,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        self.users.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        doc = self.users.find_one({"email": email.lower().strip()})
        if not doc:
            return None
        doc.pop("_id", None)
        return doc

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self.users.find_one({"user_id": user_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return doc

    def list_users(self) -> List[Dict[str, Any]]:
        cursor = self.users.find().sort("created_at", DESCENDING)
        results = []
        for doc in cursor:
            doc.pop("_id", None)
            results.append(doc)
        return results

    def toggle_user_status(self, user_id: str) -> bool:
        user = self.users.find_one({"user_id": user_id})
        if not user:
            return False
        new_status = not user.get("is_active", True)
        self.users.update_one({"user_id": user_id}, {"$set": {"is_active": new_status}})
        return True

    def get_admin_stats(self) -> Dict[str, Any]:
        analyses = self.list_analyses(limit=100)
        users = self.list_users()

        total_users = len(users)
        active_users = sum(1 for u in users if u.get("is_active"))
        total_analyses = self.analyses.count_documents({})

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

    def generate_id(self) -> str:
        return uuid.uuid4().hex[:8]
