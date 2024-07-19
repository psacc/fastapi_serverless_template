from fastapi.testclient import TestClient

from project.app import app
import os
import schemathesis
import httpx


e2e_test_url = os.getenv("E2E_TEST_URL")
url_prefix = os.environ.get("URL_PREFIX", "https://myservice.dev").rstrip("/")


if e2e_test_url:
    e2e_test_url = e2e_test_url.rstrip("/")
    client = httpx.Client(base_url=e2e_test_url)
    schema = schemathesis.from_uri(f"{e2e_test_url}/openapi.json")
else:
    client = TestClient(app)
    schema = schemathesis.from_asgi("/openapi.json", app)


# TODO add a sample test
def test_encode_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["url_prefix"] == url_prefix


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
