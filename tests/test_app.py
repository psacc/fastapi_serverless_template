from fastapi.testclient import TestClient

from finn_codesubmit.app import app
import os
import schemathesis
import httpx


e2e_test_url = os.getenv("E2E_TEST_URL")
base_url = os.environ.get("URL_PREFIX", "https://myservice.dev").rstrip("/")

if e2e_test_url:
    e2e_test_url = e2e_test_url.rstrip("/")
    client = httpx.Client(base_url=e2e_test_url)
    schema = schemathesis.from_uri(f"{e2e_test_url}/openapi.json")
else:
    client = TestClient(app)
    schema = schemathesis.from_asgi("/openapi.json", app)


def test_encode_endpoint():
    response = client.post("/encode", json={"url": "https://www.google.com"})
    assert response.status_code == 200
    assert "shortUrl" in response.json()
    assert isinstance(response.json()["shortUrl"], str)
    assert response.json()["shortUrl"] == f"{base_url}/49CcFSu5tcoFwK"


def test_decode_endpoint():
    client.post("/encode", json={"url": "https://www.google.com"})
    response = client.post("/decode", json={"url": f"{base_url}/49CcFSu5tcoFwK"})
    assert response.status_code == 200
    assert "originalUrl" in response.json()
    assert isinstance(response.json()["originalUrl"], str)
    assert response.json()["originalUrl"] == "https://www.google.com"


def test_invalid_encode_long_url():
    response = client.post("/encode", json={"url": "this is not an url"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Bad URL: 'this is not an url'"}


def test_invalid_decode_short_url():
    response = client.post(
        "/decode", json={"url": "https://wrongservice.dev/49CcFSu5tcoFwK"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Bad short URL: 'https://wrongservice.dev/49CcFSu5tcoFwK'"
    }


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
