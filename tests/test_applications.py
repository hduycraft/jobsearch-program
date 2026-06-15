from fastapi.testclient import TestClient


def _create_job(client: TestClient) -> int:
    response = client.post(
        "/jobs",
        json={"title": "Backend Developer", "company": "Example Co"},
    )
    return response.json()["id"]


def test_create_application_for_job(client: TestClient) -> None:
    job_id = _create_job(client)

    response = client.post(
        "/applications",
        json={
            "job_id": job_id,
            "status": "interested",
            "notes": "Looks aligned with Python API work.",
            "next_action": "Tailor CV",
            "deadline": "2026-06-30T09:00:00Z",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["job_id"] == job_id
    assert data["status"] == "interested"
    assert data["notes"] == "Looks aligned with Python API work."
    assert data["next_action"] == "Tailor CV"
    assert data["deadline"].startswith("2026-06-30T09:00:00")
    assert data["applied_at"] is None
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_application_defaults_to_saved_status(client: TestClient) -> None:
    job_id = _create_job(client)

    response = client.post("/applications", json={"job_id": job_id})

    assert response.status_code == 201
    assert response.json()["status"] == "saved"


def test_list_applications_returns_created_applications(client: TestClient) -> None:
    first_job_id = _create_job(client)
    second_job_response = client.post(
        "/jobs",
        json={"title": "Data Engineer", "company": "Data Co"},
    )
    second_job_id = second_job_response.json()["id"]
    client.post("/applications", json={"job_id": first_job_id, "status": "saved"})
    client.post(
        "/applications",
        json={"job_id": second_job_id, "status": "applied"},
    )

    response = client.get("/applications")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["job_id"] == first_job_id
    assert data[1]["job_id"] == second_job_id


def test_get_application_by_id(client: TestClient) -> None:
    job_id = _create_job(client)
    create_response = client.post(
        "/applications",
        json={"job_id": job_id, "status": "cv_tailored"},
    )
    application_id = create_response.json()["id"]

    response = client.get(f"/applications/{application_id}")

    assert response.status_code == 200
    assert response.json()["id"] == application_id
    assert response.json()["status"] == "cv_tailored"


def test_patch_application_updates_only_sent_fields(client: TestClient) -> None:
    job_id = _create_job(client)
    create_response = client.post(
        "/applications",
        json={
            "job_id": job_id,
            "status": "interested",
            "notes": "Initial notes",
        },
    )
    application_id = create_response.json()["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={
            "status": "applied",
            "next_action": "Prepare for recruiter screen",
            "applied_at": "2026-06-15T10:00:00Z",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "applied"
    assert data["notes"] == "Initial notes"
    assert data["next_action"] == "Prepare for recruiter screen"
    assert data["applied_at"].startswith("2026-06-15T10:00:00")


def test_create_application_requires_existing_job(client: TestClient) -> None:
    response = client.post("/applications", json={"job_id": 999})

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_create_application_rejects_duplicate_for_job(client: TestClient) -> None:
    job_id = _create_job(client)
    client.post("/applications", json={"job_id": job_id})

    response = client.post("/applications", json={"job_id": job_id})

    assert response.status_code == 409
    assert response.json()["detail"] == "Application already exists for this job"


def test_deleting_job_removes_application_tracking(client: TestClient) -> None:
    job_id = _create_job(client)
    create_response = client.post("/applications", json={"job_id": job_id})
    application_id = create_response.json()["id"]

    delete_response = client.delete(f"/jobs/{job_id}")
    get_response = client.get(f"/applications/{application_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_missing_application_returns_404(client: TestClient) -> None:
    response = client.get("/applications/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"
