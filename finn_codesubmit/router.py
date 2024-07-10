import os
from fastapi import HTTPException
from openapi_to_fastapi.routes import SpecRouter
from pydantic import BaseModel

from finn_codesubmit.datastore import InMemoryDataStore
from finn_codesubmit.logger import get_logger
from finn_codesubmit.url_shortener import UrlShortener

logger = get_logger(__name__)

stage = os.environ.get("STAGE", "dev")
url_prefix = os.environ.get("URL_PREFIX", "https://myservice.dev").rstrip("/")
api_spec_path = os.environ.get("API_SPEC_PATH", "./finn_codesubmit/api-spec")

spec_router = SpecRouter(api_spec_path)


url_shortener = UrlShortener(url_prefix=url_prefix, datastore=InMemoryDataStore())


class ErrorResponseModel(BaseModel):
    detail: str


def name_factory(path: str, **kwargs):
    return path.replace("/", " ").strip()


@spec_router.post(
    "/encode", name_factory=name_factory, responses={400: {"model": ErrorResponseModel}}
)
async def encode(params):
    url = params.url
    try:
        encodedUrl = await url_shortener.shorten_url(url)
        return {"shortUrl": encodedUrl}
    except KeyError as e:
        logger.info(f"Bad URL: {url}, cause KeyError: {e}")
        raise HTTPException(detail=f"Bad URL: '{url}'", status_code=400)


@spec_router.post(
    "/decode", name_factory=name_factory, responses={400: {"model": ErrorResponseModel}}
)
async def decode(params):
    url = params.url
    try:
        originalUrl = await url_shortener.get_long_url(url)
        return {"originalUrl": originalUrl}
    except KeyError as e:
        logger.info(f"Bad URL: {url}, cause KeyError: {e}")
        raise HTTPException(detail=f"Bad short URL: '{url}'", status_code=400)


router = spec_router.to_fastapi_router()

logger.info(f"Router created with {len(router.routes)} routes for stage: {stage}")
