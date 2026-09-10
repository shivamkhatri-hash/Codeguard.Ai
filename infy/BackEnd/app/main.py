from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.code import router as code_router
from app.api.analysis import router as analysis_router
from app.api.remediation import router as remediation_router
from app.api.summary import router as summary_router
from app.api.assistant import router as assistant_router
from app.api.report import router as report_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the Smart Code Inspection Platform. Handles submission and validation of code files.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to keep internal details secure and unexposed
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."}
    )

# Register endpoints under '/api' prefix
app.include_router(code_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(remediation_router, prefix="/api")
app.include_router(summary_router, prefix="/api")
app.include_router(assistant_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API. Please navigate to /docs for interactive testing."
    }
