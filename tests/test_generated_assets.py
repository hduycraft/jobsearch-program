from fastapi.testclient import TestClient


def _create_job(client: TestClient, title: str = "Backend Developer") -> int:
    response = client.post(
        "/jobs",
        json={"title": title, "company": "Example Co"},
    )
    return response.json()["id"]


def test_create_generated_asset_for_job(client: TestClient) -> None:
    job_id = _create_job(client)

    response = client.post(
        f"/jobs/{job_id}/generated-assets",
        json={
            "asset_type": "cv_suggestions",
            "title": "CV suggestions for Backend Developer",
            "content": {
                "tailored_summary_suggestion": "Emphasize Python API work.",
                "projects_to_highlight": ["CareerMatch Assistant"],
            },
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["job_id"] == job_id
    assert data["asset_type"] == "cv_suggestions"
    assert data["title"] == "CV suggestions for Backend Developer"
    assert data["content"] == {
        "tailored_summary_suggestion": "Emphasize Python API work.",
        "projects_to_highlight": ["CareerMatch Assistant"],
    }
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_list_generated_assets_for_job(client: TestClient) -> None:
    first_job_id = _create_job(client)
    second_job_id = _create_job(client, title="Data Engineer")
    client.post(
        f"/jobs/{first_job_id}/generated-assets",
        json={
            "asset_type": "cv_suggestions",
            "content": {"summary": "First job CV notes"},
        },
    )
    client.post(
        f"/jobs/{first_job_id}/generated-assets",
        json={
            "asset_type": "interview_prep",
            "title": "Interview prep",
            "content": {"study_topics": ["FastAPI", "PostgreSQL"]},
        },
    )
    client.post(
        f"/jobs/{second_job_id}/generated-assets",
        json={
            "asset_type": "cover_letter",
            "content": {"draft": "Second job cover letter"},
        },
    )

    response = client.get(f"/jobs/{first_job_id}/generated-assets")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["job_id"] == first_job_id
    assert data[0]["asset_type"] == "cv_suggestions"
    assert data[1]["job_id"] == first_job_id
    assert data[1]["asset_type"] == "interview_prep"


def test_create_generated_asset_requires_existing_job(client: TestClient) -> None:
    response = client.post(
        "/jobs/999/generated-assets",
        json={
            "asset_type": "interview_prep",
            "content": {"study_topics": ["Python"]},
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_list_generated_assets_requires_existing_job(client: TestClient) -> None:
    response = client.get("/jobs/999/generated-assets")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_generated_asset_requires_known_type(client: TestClient) -> None:
    job_id = _create_job(client)

    response = client.post(
        f"/jobs/{job_id}/generated-assets",
        json={
            "asset_type": "job_summary",
            "content": {"summary": "Unsupported for Phase 10"},
        },
    )

    assert response.status_code == 422


def test_deleting_job_removes_generated_assets(client: TestClient) -> None:
    job_id = _create_job(client)
    client.post(
        f"/jobs/{job_id}/generated-assets",
        json={
            "asset_type": "interview_prep",
            "content": {"study_topics": ["FastAPI"]},
        },
    )

    delete_response = client.delete(f"/jobs/{job_id}")
    list_response = client.get(f"/jobs/{job_id}/generated-assets")

    assert delete_response.status_code == 204
    assert list_response.status_code == 404
