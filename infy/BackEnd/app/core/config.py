import os
from typing import List
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Smart Code Inspection Platform"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Security & Validation Limits
    MAX_FILE_SIZE_BYTES: int = 1024 * 1024 * 1  # 1MB limit for code submission demo
    ALLOWED_EXTENSIONS: List[str] = [".py", ".java", ".js", ".ts", ".cpp", ".cc", ".h", ".go", ".html", ".htm"]
    ALLOWED_LANGUAGES: List[str] = ["python", "java", "javascript", "typescript", "cpp", "go", "html"]

settings = Settings()
