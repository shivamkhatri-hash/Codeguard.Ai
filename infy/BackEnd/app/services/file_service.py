import os
from typing import Tuple
from fastapi import UploadFile
from app.core.config import settings

class FileService:
    @staticmethod
    def validate_file_metadata(file: UploadFile) -> Tuple[bool, str]:
        """
        Validates file extension.
        """
        filename = file.filename or ""
        _, ext = os.path.splitext(filename)
        if ext.lower() not in settings.ALLOWED_EXTENSIONS:
            return False, f"Unsupported file extension '{ext}'. Only {', '.join(settings.ALLOWED_EXTENSIONS)} are allowed."
        return True, ""

    @staticmethod
    async def extract_content_and_validate_size(file: UploadFile) -> Tuple[str, str]:
        """
        Reads file content, verifies size constraints, decodes it to a string,
        and identifies the language from the extension.
        """
        # Read content bytes
        content_bytes = await file.read()
        
        # Reset file pointer for any future operations
        await file.seek(0)
        
        if len(content_bytes) == 0:
            raise ValueError("Uploaded file is empty")
            
        if len(content_bytes) > settings.MAX_FILE_SIZE_BYTES:
            limit_mb = settings.MAX_FILE_SIZE_BYTES / (1024 * 1024)
            raise ValueError(f"Uploaded file size exceeds the limit of {limit_mb:.1f} MB")
            
        # Decode the bytes to a string
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                # Fallback decoder
                content = content_bytes.decode("latin-1")
            except Exception:
                raise ValueError("Could not decode file content. Please upload a valid text-based source file.")
                
        # Determine language based on extension
        filename = file.filename or ""
        _, ext = os.path.splitext(filename)
        ext_lower = ext.lower()
        
        # Mapping extension to language
        if ext_lower == ".py":
            language = "python"
        elif ext_lower == ".java":
            language = "java"
        elif ext_lower == ".js":
            language = "javascript"
        elif ext_lower == ".ts":
            language = "typescript"
        elif ext_lower in (".cpp", ".cc", ".h"):
            language = "cpp"
        elif ext_lower == ".go":
            language = "go"
        elif ext_lower in (".html", ".htm"):
            language = "html"
        else:
            raise ValueError(f"Unsupported file extension '{ext}'")
            
        return content, language

file_service = FileService()
