from fastapi.testclient import TestClient

from finn_codesubmit.app import app

client = TestClient(app)


def test_encode_endpoint():
    response = client.post("/encode/", params={"url": "https://www.google.com"})
    assert response.status_code == 200
    # assert "short_url" in response.json()


def test_decode_endpoint():
    response = client.post("/decode/", params={"url": "https://www.google.com"})
    assert response.status_code == 200
    # assert "original_url" in response.json()
