import os
from openapi_to_fastapi.routes import SpecRouter

from finn_codesubmit.datastore import InMemoryDataStore
from finn_codesubmit.url_shortener import UrlShortener

stage = os.environ.get("STAGE", "dev")
url_prefix = os.environ.get("URL_PREFIX", "https://myservice.dev")
api_spec_path = os.environ.get("API_SPEC_PATH", "./api-spec")

spec_router = SpecRouter(api_spec_path)


url_shortener = UrlShortener(url_prefix=url_prefix, datastore=InMemoryDataStore())


@spec_router.post("/encode")
async def encode(url: str):
    encodedUrl = await url_shortener.shorten_url(url)
    return {"shortUrl": encodedUrl}


@spec_router.post("/decode")
async def decode(url: str):
    originalUrl = await url_shortener.get_long_url(url)
    return {"originalUrl": originalUrl}


router = spec_router.to_fastapi_router()
