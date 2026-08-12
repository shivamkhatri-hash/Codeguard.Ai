import uuid
from typing import Dict, Any, Optional

class InMemStorageService:
    def __init__(self):
        # Maps analysis_id -> analysis data dict
        self._store: Dict[str, Dict[str, Any]] = {}

    def save_analysis(self, analysis_id: str, data: Dict[str, Any]) -> None:
        self._store[analysis_id] = data

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(analysis_id)

    def generate_id(self) -> str:
        # Generates a unique 8-character ID for analysis
        return uuid.uuid4().hex[:8]

storage_service = InMemStorageService()
