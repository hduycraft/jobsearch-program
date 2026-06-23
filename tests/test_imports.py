from fastapi.testclient import TestClient


def test_import_manual_jobs_creates_jobs(client: TestClient) -> None:
    response = client.post(
        "/imports/jobs",
        json={
            "source_name": "manual-bulk-import",
            "jobs": [
                {
                    "title": "  Backend   Developer ",
                    "company": " Example Co ",
                    "location": "Remote",
                    "source_url": "https://example.com/jobs/backend-developer",
                    "description": "Build APIs with Python.",
                    "requirements": [" Python ", "FastAPI", "python"],
                    "seniority": " mid ",
                },
                {
                    "title": "Data Engineer",
                    "company": "Data Co",
                    "location": "Singapore",
                    "source_url": "https://example.com/jobs/data-engineer",
                },
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["source_name"] == "manual-bulk-import"
    assert data["imported_count"] == 2
    assert data["skipped_count"] == 0

    first_job = data["imported_jobs"][0]
    assert first_job["title"] == "Backend Developer"
    assert first_job["company"] == "Example Co"
    assert first_job["location"] == "Remote"
    assert first_job["source"] == "manual-bulk-import"
    assert first_job["source_url"] == "https://example.com/jobs/backend-developer"
    assert first_job["requirements"] == ["Python", "FastAPI"]
    assert first_job["seniority"] == "mid"

    second_job = data["imported_jobs"][1]
    assert second_job["title"] == "Data Engineer"
    assert second_job["location"] == "Singapore"


def test_import_manual_jobs_defaults_source_name(client: TestClient) -> None:
    response = client.post(
        "/imports/jobs",
        json={
            "jobs": [
                {
                    "title": "Backend Developer",
                    "company": "Example Co",
                    "location": "Remote",
                }
            ],
        },
    )

    assert response.status_code == 201
    assert response.json()["source_name"] == "manual"
    assert response.json()["imported_jobs"][0]["source"] == "manual"


def test_import_manual_jobs_skips_duplicates(client: TestClient) -> None:
    client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "location": "Remote",
            "source_url": "https://example.com/jobs/backend-developer",
        },
    )

    response = client.post(
        "/imports/jobs",
        json={
            "source_name": "manual-bulk-import",
            "jobs": [
                {
                    "title": "Backend Developer",
                    "company": "Example Co",
                    "location": "Remote",
                    "source_url": "https://example.com/jobs/backend-developer",
                },
                {
                    "title": "Backend Developer",
                    "company": "Example Co",
                    "location": "Hybrid",
                    "source_url": "https://example.com/jobs/backend-developer-copy",
                },
                {
                    "title": "Frontend Developer",
                    "company": "Example Co",
                    "location": "Onsite",
                    "source_url": "https://example.com/jobs/frontend-developer",
                },
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["imported_count"] == 1
    assert data["skipped_count"] == 2
    assert [job["reason"] for job in data["skipped_jobs"]] == [
        "duplicate",
        "duplicate",
    ]
    assert data["imported_jobs"][0]["title"] == "Frontend Developer"


def test_import_manual_jobs_requires_at_least_one_job(client: TestClient) -> None:
    response = client.post(
        "/imports/jobs",
        json={
            "source_name": "manual-bulk-import",
            "jobs": [],
        },
    )

    assert response.status_code == 422
