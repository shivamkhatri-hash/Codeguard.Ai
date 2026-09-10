import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):

    PROJECT_NAME: str = "Smart Code Inspection Platform"

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,*"
        ).split(",") if origin.strip()
    ]

    # Security & Validation Limits
    MAX_FILE_SIZE_BYTES: int = 1024 * 1024 * 1  # 1MB limit for code submission demo

    ALLOWED_EXTENSIONS: List[str] = [
        ".py",
        ".java",
        ".js",
        ".ts",
        ".cpp",
        ".cc",
        ".h",
        ".go",
        ".html",
        ".htm",
    ]

    ALLOWED_LANGUAGES: List[str] = [
        "python",
        "java",
        "javascript",
        "typescript",
        "cpp",
        "go",
        "html",
    ]

    # Gemini LLM Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


settings = Settings()