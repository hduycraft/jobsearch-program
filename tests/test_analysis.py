from fastapi.testclient import TestClient


def test_analyze_job_description_extracts_skills_and_seniority(
    client: TestClient,
) -> None:
    response = client.post(
        "/analysis/job",
        json={
            "description": (
                "Senior Backend Developer required. "
                "Must have 5+ years experience with Python, FastAPI, REST APIs, "
                "PostgreSQL, Docker, Azure DevOps, and Git."
            ),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["extracted_skills"] == [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "Azure",
        "Azure DevOps",
        "Git",
        "REST API",
    ]
    assert data["seniority_estimate"] == "senior"
    assert data["requirements_summary"] == [
        "Senior Backend Developer required.",
        (
            "Must have 5+ years experience with Python, FastAPI, REST APIs, "
            "PostgreSQL, Docker, Azure DevOps, and Git."
        ),
    ]


def test_analyze_job_description_extracts_ai_and_frontend_skills(
    client: TestClient,
) -> None:
    response = client.post(
        "/analysis/job",
        json={
            "description": (
                "We are looking for a mid-level engineer to build React and "
                "Next.js tools using Machine Learning, NLP, RAG, and LLM workflows."
            ),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["extracted_skills"] == [
        "Machine Learning",
        "NLP",
        "RAG",
        "LLM",
        "React",
        "Next.js",
    ]
    assert data["seniority_estimate"] == "mid-level"
    assert data["requirements_summary"] == [
        (
            "We are looking for a mid-level engineer to build React and Next.js "
            "tools using Machine Learning, NLP, RAG, and LLM workflows."
        ),
    ]


def test_analyze_job_description_can_estimate_seniority_from_years(
    client: TestClient,
) -> None:
    response = client.post(
        "/analysis/job",
        json={
            "description": (
                "Developer role. Need 3 years experience designing APIs with SQL."
            ),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["extracted_skills"] == ["SQL"]
    assert data["seniority_estimate"] == "mid-level"


def test_analyze_job_description_requires_description(client: TestClient) -> None:
    response = client.post("/analysis/job", json={})

    assert response.status_code == 422


def test_match_profile_to_job_returns_explainable_score(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={
            "target_roles": ["Backend Developer", "AI Engineer"],
            "skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker"],
            "projects": [
                {
                    "name": "CareerMatch Assistant",
                    "description": "Job search API with profile matching.",
                    "skills": ["FastAPI", "PostgreSQL"],
                },
            ],
        },
    )
    job_response = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "description": (
                "Senior Backend Developer required. Must have Python, FastAPI, "
                "PostgreSQL, Docker, Azure DevOps, and REST API experience."
            ),
            "requirements": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "seniority": "senior",
        },
    )

    response = client.post(
        "/analysis/match",
        json={
            "profile_id": profile_response.json()["id"],
            "job_id": job_response.json()["id"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 60
    assert data["score_breakdown"] == {
        "skill_match": 34,
        "target_role_match": 20,
        "project_relevance": 6,
    }
    assert data["matched_skills"] == ["Python", "FastAPI", "PostgreSQL", "Docker"]
    assert data["missing_skills"] == ["Azure", "Azure DevOps", "REST API"]
    assert data["strengths"] == [
        "Profile matches required skills: Python, FastAPI, PostgreSQL, Docker.",
        "Target role aligns with this job: Backend Developer.",
        "Profile projects show relevant experience with FastAPI, PostgreSQL.",
    ]
    assert data["gaps"] == [
        "Job mentions skills not listed in the profile: Azure, Azure DevOps, REST API."
    ]
    assert data["recommendation"] == "Good match. Review the gaps before tailoring the CV."


def test_match_profile_to_job_returns_404_for_missing_profile(
    client: TestClient,
) -> None:
    job_response = client.post(
        "/jobs",
        json={"title": "Backend Developer", "company": "Example Co"},
    )

    response = client.post(
        "/analysis/match",
        json={"profile_id": 999, "job_id": job_response.json()["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_match_profile_to_job_returns_404_for_missing_job(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={"target_roles": ["Backend Developer"], "skills": ["Python"]},
    )

    response = client.post(
        "/analysis/match",
        json={"profile_id": profile_response.json()["id"], "job_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_openapi_schema_includes_analysis_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/analysis/job" in response.json()["paths"]
    assert "/analysis/match" in response.json()["paths"]
