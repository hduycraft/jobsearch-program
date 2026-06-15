from fastapi.testclient import TestClient


def test_create_job(client: TestClient) -> None:
    response = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "location": "Remote",
            "source": "manual",
            "source_url": "https://example.com/jobs/backend-developer",
            "description": "Build APIs with Python and FastAPI.",
            "requirements": ["Python", "FastAPI", "REST API"],
            "seniority": "mid",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Backend Developer"
    assert data["company"] == "Example Co"
    assert data["requirements"] == ["Python", "FastAPI", "REST API"]
    assert data["date_found"] is not None
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_list_jobs_returns_created_jobs(client: TestClient) -> None:
    client.post("/jobs", json={"title": "Backend Developer", "company": "Example Co"})
    client.post("/jobs", json={"title": "Data Engineer", "company": "Data Co"})

    response = client.get("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Backend Developer"
    assert data[1]["title"] == "Data Engineer"


def test_get_job_by_id(client: TestClient) -> None:
    create_response = client.post(
        "/jobs",
        json={"title": "Backend Developer", "company": "Example Co"},
    )
    job_id = create_response.json()["id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id
    assert response.json()["title"] == "Backend Developer"


def test_patch_job_updates_only_sent_fields(client: TestClient) -> None:
    create_response = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "location": "Remote",
        },
    )
    job_id = create_response.json()["id"]

    response = client.patch(
        f"/jobs/{job_id}",
        json={"location": "Bangkok", "requirements": ["Python", "SQL"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Backend Developer"
    assert data["company"] == "Example Co"
    assert data["location"] == "Bangkok"
    assert data["requirements"] == ["Python", "SQL"]


def test_delete_job_removes_it(client: TestClient) -> None:
    create_response = client.post(
        "/jobs",
        json={"title": "Backend Developer", "company": "Example Co"},
    )
    job_id = create_response.json()["id"]

    delete_response = client.delete(f"/jobs/{job_id}")
    get_response = client.get(f"/jobs/{job_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_missing_job_returns_404(client: TestClient) -> None:
    response = client.get("/jobs/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
