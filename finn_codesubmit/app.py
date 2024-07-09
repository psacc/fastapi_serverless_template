import os

from fastapi import FastAPI

from finn_codesubmit.datastore import InMemoryDataStore
from finn_codesubmit.url_shortener import UrlShortener

stage = os.environ.get("STAGE", "dev")
url_prefix = os.environ.get("URL_PREFIX", "myservice.dev")


app = FastAPI()
url_shortener = UrlShortener(url_prefix=url_prefix, datastore=InMemoryDataStore())


@app.post("/encode/")
async def encode():
    url = "https://www.google.com"
    encodedUrl = await url_shortener.shorten_url(url)
    return {"encodedUrl": encodedUrl}


@app.post("/decode/")
async def decode():
    url = "https://myservice.dev/abc123"
    originalUrl = await url_shortener.get_long_url(url)
    return {"originalUrl": originalUrl}
