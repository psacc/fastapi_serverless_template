from typing import Optional
import validators
import base62

from finn_codesubmit.datastore import DataStore
import hashlib

MAX_COLLISION_RETRIES = 1000


class UrlShortener:
    def __init__(self, url_prefix: str, datastore: DataStore):
        self.url_prefix = url_prefix
        self.datastore = datastore

    async def shorten_url(self, long_url: str) -> str:
        """
        Get the short URL for a given long URL. The function is idempotent,
        as long as there are no deletions from the datastore.

        Args:
            long_url: The long URL to shorten

        Returns:
            The short URL

        Raises:
            KeyError: If the provided short URL is invalid
        """
        if not validators.url(long_url):
            raise KeyError("Invalid short URL")

        iteration: int = 0
        while iteration < MAX_COLLISION_RETRIES:
            short_code: str = await self.generate_short_code(long_url, iteration)
            iteration += 1
            try:
                await self.datastore.insert(short_code, long_url)
            except KeyError:
                if not await self.datastore.read(short_code) == long_url:
                    continue
            return f"{self.url_prefix}/{short_code}"

        raise KeyError("Failed to generate a unique short URL")

    async def generate_short_code(self, url: str, iteration: int = 0) -> str:
        data = f"{url}{iteration}".encode()
        hash_object = hashlib.sha256(data)

        hash_bytes = hash_object.digest()[:10]
        return base62.encodebytes(hash_bytes)

    async def get_long_url(self, short_url: str) -> Optional[str]:
        """
        Get the long URL for a given short URL

        Args:
            short_url: The short URL to look up

        Returns:
            The long URL if found, otherwise None

        Raises:
            KeyError: If the short URL is not found in the datastore, or the provided short URL is invalid
        """
        if not validators.url(short_url) or not short_url.startswith(self.url_prefix):
            raise KeyError("Invalid short URL")

        short_code: str = short_url.split("/")[-1]

        return f"{await self.datastore.read(short_code)}" or None
