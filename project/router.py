import os
from fastapi import APIRouter

from .logger import get_logger

logger = get_logger(__name__)

stage = os.environ.get("STAGE", "dev")
url_prefix = os.environ.get("URL_PREFIX", "https://myservice.dev").rstrip("/")

router = APIRouter()


@router.get("/health")
async def heath():
    return {"status": "ok", "stage": stage, "url_prefix": url_prefix}


logger.info(f"Router created with {len(router.routes)} routes for stage: {stage}")
