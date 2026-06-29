from fastapi.testclient import TestClient


def test_frontend_homepage_loads(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "CareerMatch Assistant" in response.text
    assert "/static/app.js" in response.text
    assert "/static/styles.css" in response.text


def test_frontend_static_assets_load(client: TestClient) -> None:
    script_response = client.get("/static/app.js")
    style_response = client.get("/static/styles.css")

    assert script_response.status_code == 200
    assert "javascript" in script_response.headers["content-type"]
    assert "async function loadData" in script_response.text
    assert style_response.status_code == 200
    assert "text/css" in style_response.headers["content-type"]
    assert ".app-header" in style_response.text
