import schemathesis
from fastapi.testclient import TestClient

from finn_codesubmit.app import app

client = TestClient(app)


def test_encode_endpoint():
    response = client.post("/encode/", params={"url": "https://www.google.com"})
    assert response.status_code == 200
    assert "shortUrl" in response.json()
    assert isinstance(response.json()["shortUrl"], str)
    assert response.json()["shortUrl"] == "https://myservice.dev/49CcFSu5tcoFwK"


def test_decode_endpoint():
    client.post("/encode/", params={"url": "https://www.google.com"})
    response = client.post(
        "/decode/", params={"url": "https://myservice.dev/49CcFSu5tcoFwK"}
    )
    assert response.status_code == 200
    assert "originalUrl" in response.json()
    assert isinstance(response.json()["originalUrl"], str)
    assert response.json()["originalUrl"] == "https://www.google.com"


def test_invalid_encode_long_url():
    response = client.post("/encode/", params={"url": "this is not an url"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Bad URL: this is not an url"}


def test_invalid_decode_short_url():
    response = client.post(
        "/decode/", params={"url": "https://wrongservice.dev/49CcFSu5tcoFwK"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Bad short URL: https://wrongservice.dev/49CcFSu5tcoFwK"
    }


schema = schemathesis.from_asgi("/openapi.json", app)


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
