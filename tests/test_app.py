from fastapi.testclient import TestClient

from finn_codesubmit.app import app

client = TestClient(app)


def test_encode_endpoint():
    response = client.post("/encode/", json={"url": "https://www.example.com"})
    assert response.status_code == 200
    # assert "short_url" in response.json()


def test_decode_endpoint():
    response = client.post("/decode/", json={"short_url": "abc123"})
    assert response.status_code == 200
    # assert "original_url" in response.json()
