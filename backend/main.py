from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from infrastructure.config import get_settings
from infrastructure.dependencies import close_httpx_client, get_genai_client
from infrastructure.logging import get_logger
from api.v1 import router as api_v1_router
from utils.errors import DatasmithError


settings = get_settings()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", environment=settings.environment)

    if not settings.google_api_key:
        logger.warning("google_api_key_missing")
    else:
        get_genai_client()

    yield

    await close_httpx_client()
    logger.info("shutdown")


app = FastAPI(
    title="Datasmith AI API",
    description="AI-powered document analysis and content extraction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


@app.exception_handler(DatasmithError)
async def datasmith_error_handler(request: Request, exc: DatasmithError):
    logger.error("datasmith_error", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", error=str(exc), path=request.url.path, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "llm_model": settings.llm_model
    }


@app.get("/")
async def root():
    return {
        "service": "Datasmith AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

