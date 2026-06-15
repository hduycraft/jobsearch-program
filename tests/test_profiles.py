from fastapi.testclient import TestClient


def _profile_payload() -> dict[str, object]:
    return {
        "target_roles": ["Backend Developer", "AI Engineer"],
        "skills": ["Python", "FastAPI", "SQL"],
        "experience_summary": "Builds APIs and automation for job search workflows.",
        "projects": [
            {
                "name": "CareerMatch Assistant",
                "description": "Human-in-the-loop job search assistant.",
                "skills": ["FastAPI", "SQLAlchemy"],
                "url": "https://example.com/careermatch",
            },
        ],
    }


def test_create_profile(client: TestClient) -> None:
    response = client.post("/profiles", json=_profile_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["target_roles"] == ["Backend Developer", "AI Engineer"]
    assert data["skills"] == ["Python", "FastAPI", "SQL"]
    assert data["experience_summary"].startswith("Builds APIs")
    assert data["projects"][0]["name"] == "CareerMatch Assistant"
    assert data["projects"][0]["skills"] == ["FastAPI", "SQLAlchemy"]
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_profile_defaults_optional_fields(client: TestClient) -> None:
    response = client.post("/profiles", json={})

    assert response.status_code == 201
    data = response.json()
    assert data["target_roles"] == []
    assert data["skills"] == []
    assert data["experience_summary"] is None
    assert data["projects"] == []


def test_list_profiles_returns_created_profiles(client: TestClient) -> None:
    client.post("/profiles", json=_profile_payload())
    client.post(
        "/profiles",
        json={
            "target_roles": ["Data Engineer"],
            "skills": ["Python", "PostgreSQL"],
        },
    )

    response = client.get("/profiles")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["target_roles"] == ["Backend Developer", "AI Engineer"]
    assert data[1]["target_roles"] == ["Data Engineer"]


def test_get_profile_by_id(client: TestClient) -> None:
    create_response = client.post("/profiles", json=_profile_payload())
    profile_id = create_response.json()["id"]

    response = client.get(f"/profiles/{profile_id}")

    assert response.status_code == 200
    assert response.json()["id"] == profile_id
    assert response.json()["skills"] == ["Python", "FastAPI", "SQL"]


def test_patch_profile_updates_only_sent_fields(client: TestClient) -> None:
    create_response = client.post("/profiles", json=_profile_payload())
    profile_id = create_response.json()["id"]

    response = client.patch(
        f"/profiles/{profile_id}",
        json={
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "projects": [
                {
                    "name": "Job Matching API",
                    "skills": ["FastAPI", "NLP"],
                },
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["target_roles"] == ["Backend Developer", "AI Engineer"]
    assert data["skills"] == ["Python", "FastAPI", "PostgreSQL", "Docker"]
    assert data["projects"][0]["name"] == "Job Matching API"
    assert data["projects"][0]["description"] is None


def test_missing_profile_returns_404(client: TestClient) -> None:
    response = client.get("/profiles/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"
