from fastapi.testclient import TestClient


def test_swagger_docs_load(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "swagger-ui" in response.text.lower()


def test_openapi_schema_includes_health_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()
    assert schema["info"]["title"] == "CareerMatch Assistant"
    assert schema["info"]["version"] == "0.1.0"
    assert "/health" in schema["paths"]
    assert "get" in schema["paths"]["/health"]
