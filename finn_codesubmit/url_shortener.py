from typing import Optional

from finn_codesubmit.datastore import DataStore


class UrlShortener:
    def __init__(self, url_prefix: str, datastore: DataStore):
        self.url_prefix = url_prefix
        self.datastore = datastore

    async def shorten_url(self, long_url: str) -> str:
        short_code: str = await self.generate_short_code()

        # TODO handle collisions
        await self.datastore.insert(short_code, long_url)

        return f"{self.url_prefix}/{short_code}"

    async def generate_short_code(self) -> str:
        # TODO
        # Implement your logic to generate a unique short code
        # This can be a random string, a hash, or any other method you prefer
        # Make sure the generated code is unique and not already in use

        # Placeholder implementation
        return "abc123"

    async def get_long_url(self, short_url: str) -> Optional[str]:
        short_code: str = short_url.split("/")[-1]

        return f"{await self.datastore.read(short_code)}" or None
