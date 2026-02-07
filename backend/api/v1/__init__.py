from fastapi import APIRouter
from .routes import analyze, extract, health


router = APIRouter()

router.include_router(analyze.router, tags=["Analysis"])
router.include_router(extract.router, tags=["Extraction"])
router.include_router(health.router, tags=["Health"])
