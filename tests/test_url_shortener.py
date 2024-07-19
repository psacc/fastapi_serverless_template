import pytest

from finn_codesubmit.datastore import InMemoryDataStore
from finn_codesubmit.url_shortener import UrlShortener


@pytest.fixture
def datastore():
    return InMemoryDataStore()


@pytest.fixture
def url_shortener(datastore):
    return UrlShortener("https://sh.test", datastore)


@pytest.mark.asyncio
async def test_shorten_url_empty_long_url(url_shortener):
    with pytest.raises(KeyError):
        await url_shortener.shorten_url("")


@pytest.mark.asyncio
async def test_get_long_url_empty_short_url(url_shortener):
    with pytest.raises(KeyError):
        await url_shortener.get_long_url("")


@pytest.mark.asyncio
async def test_get_long_url_with_invalid_url_prefix(url_shortener):
    with pytest.raises(KeyError):
        await url_shortener.get_long_url("https://example.org")


@pytest.mark.asyncio
async def test_shorten_url_idempotent(url_shortener, datastore):
    long_url = "https://cipolle.org/thisisverylong"
    await datastore.insert(url_shortener.generate_short_code(long_url), long_url)
    short_url = await url_shortener.shorten_url(long_url)

    assert short_url == "https://sh.test/4t7ftR4kyTs73L"
    assert long_url == await url_shortener.get_long_url(short_url)


@pytest.mark.asyncio
async def test_generate_short_code_is_idempotent(url_shortener):
    long_url = "https://cipolle.org/thisisverylong"
    short_code = await url_shortener.generate_short_code(long_url)
    assert short_code == await url_shortener.generate_short_code(long_url)


@pytest.mark.asyncio
async def test_shorten_url_with_collision(url_shortener, datastore):
    long_url = "https://cipolle.org/thisisverylong"
    another_long_url = "https://cipolle.org/thisisverylong_and_simualted_collision"

    await datastore.insert(
        await url_shortener.generate_short_code(another_long_url), long_url
    )

    short_url = await url_shortener.shorten_url(another_long_url)

    assert short_url == "https://sh.test/399obNliDi4CVp"
    assert another_long_url == await url_shortener.get_long_url(short_url)

    short_url = await url_shortener.shorten_url(long_url)

    assert short_url == "https://sh.test/4t7ftR4kyTs73L"
    assert long_url == await url_shortener.get_long_url(short_url)
