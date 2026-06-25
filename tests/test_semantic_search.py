from fastapi.testclient import TestClient


def test_index_jobs_for_semantic_search(client: TestClient) -> None:
    first_job = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "description": "Build FastAPI services with PostgreSQL and Docker.",
            "requirements": ["FastAPI", "PostgreSQL", "Docker"],
        },
    )
    second_job = client.post(
        "/jobs",
        json={
            "title": "Frontend Developer",
            "company": "Example Co",
            "description": "Build React dashboards with accessible UI components.",
            "requirements": ["React"],
        },
    )

    response = client.post("/semantic-search/jobs/index")

    assert response.status_code == 200
    data = response.json()
    assert data["indexed_count"] == 2
    assert data["embeddings"] == [
        {
            "job_id": first_job.json()["id"],
            "content_hash": data["embeddings"][0]["content_hash"],
            "vector_dimensions": 64,
        },
        {
            "job_id": second_job.json()["id"],
            "content_hash": data["embeddings"][1]["content_hash"],
            "vector_dimensions": 64,
        },
    ]
    assert len(data["embeddings"][0]["content_hash"]) == 64


def test_search_indexed_jobs_returns_most_similar_job_first(
    client: TestClient,
) -> None:
    backend_job = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "API Co",
            "description": "Build Python FastAPI services with PostgreSQL.",
            "requirements": ["Python", "FastAPI", "PostgreSQL"],
        },
    )
    client.post(
        "/jobs",
        json={
            "title": "Frontend Developer",
            "company": "UI Co",
            "description": "Build React dashboards and design systems.",
            "requirements": ["React"],
        },
    )
    client.post("/semantic-search/jobs/index")

    response = client.post(
        "/semantic-search/jobs/search",
        json={"query": "FastAPI PostgreSQL backend API", "limit": 2},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "FastAPI PostgreSQL backend API"
    assert data["results"][0]["job_id"] == backend_job.json()["id"]
    assert data["results"][0]["title"] == "Backend Developer"
    assert data["results"][0]["similarity_score"] > data["results"][1][
        "similarity_score"
    ]


def test_search_indexed_jobs_returns_empty_list_before_indexing(
    client: TestClient,
) -> None:
    client.post(
        "/jobs",
        json={"title": "Backend Developer", "company": "Example Co"},
    )

    response = client.post(
        "/semantic-search/jobs/search",
        json={"query": "backend", "limit": 5},
    )

    assert response.status_code == 200
    assert response.json()["results"] == []


def test_profile_context_returns_relevant_project_for_job(
    client: TestClient,
) -> None:
    profile_response = client.post(
        "/profiles",
        json={
            "target_roles": ["Backend Developer"],
            "skills": ["Python", "FastAPI", "PostgreSQL", "React"],
            "experience_summary": "Built backend APIs and frontend dashboards.",
            "projects": [
                {
                    "name": "CareerMatch Assistant",
                    "description": "FastAPI API with PostgreSQL-backed job matching.",
                    "skills": ["Python", "FastAPI", "PostgreSQL"],
                },
                {
                    "name": "Portfolio Site",
                    "description": "React site for project writeups.",
                    "skills": ["React"],
                },
            ],
        },
    )
    job_response = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "description": "Need FastAPI, PostgreSQL, and Python API experience.",
            "requirements": ["FastAPI", "PostgreSQL", "Python"],
        },
    )

    response = client.post(
        "/semantic-search/profile-context",
        json={
            "profile_id": profile_response.json()["id"],
            "job_id": job_response.json()["id"],
            "limit": 2,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["profile_id"] == profile_response.json()["id"]
    assert data["job_id"] == job_response.json()["id"]
    assert data["context_items"][0]["item_type"] == "project"
    assert data["context_items"][0]["title"] == "CareerMatch Assistant"
    assert data["context_items"][0]["skills"] == [
        "Python",
        "FastAPI",
        "PostgreSQL",
    ]


def test_profile_context_returns_404_for_missing_profile(client: TestClient) -> None:
    job_response = client.post(
        "/jobs",
        json={"title": "Backend Developer", "company": "Example Co"},
    )

    response = client.post(
        "/semantic-search/profile-context",
        json={"profile_id": 999, "job_id": job_response.json()["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_profile_context_returns_404_for_missing_job(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={"target_roles": ["Backend Developer"], "skills": ["Python"]},
    )

    response = client.post(
        "/semantic-search/profile-context",
        json={"profile_id": profile_response.json()["id"], "job_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
