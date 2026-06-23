from fastapi.testclient import TestClient

from app.main import app
from app.services.llm_provider import FakeLLMProvider, get_llm_provider


class BrokenLLMProvider:
    def enhance_cv_suggestions(
        self,
        profile: object,
        job: object,
        rule_based_suggestions: dict[str, object],
    ) -> dict[str, object] | None:
        raise RuntimeError("Provider unavailable")

    def enhance_interview_prep(
        self,
        profile: object,
        job: object,
        rule_based_prep: dict[str, object],
    ) -> dict[str, object] | None:
        raise RuntimeError("Provider unavailable")


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


def test_cv_suggestions_tailor_profile_to_job_without_inventing_experience(
    client: TestClient,
) -> None:
    profile_response = client.post(
        "/profiles",
        json={
            "target_roles": ["Backend Developer"],
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "experience_summary": (
                "Built backend APIs and database-backed tools for job-search workflows."
            ),
            "projects": [
                {
                    "name": "CareerMatch Assistant",
                    "description": "FastAPI job search API using PostgreSQL.",
                    "skills": ["FastAPI", "PostgreSQL"],
                },
                {
                    "name": "Portfolio Site",
                    "description": "Frontend site for project writeups.",
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
            "description": (
                "Backend Developer role requiring Python, FastAPI, PostgreSQL, "
                "Docker, Azure DevOps, and REST API experience."
            ),
            "requirements": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "seniority": "mid-level",
        },
    )

    response = client.post(
        "/analysis/cv-suggestions",
        json={
            "profile_id": profile_response.json()["id"],
            "job_id": job_response.json()["id"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tailored_summary_suggestion"] == (
        "Position your CV summary for the Backend Developer at Example Co role by "
        "emphasizing your experience with Python, FastAPI, PostgreSQL, and Docker, "
        "using CareerMatch Assistant (matches FastAPI and PostgreSQL) as evidence, "
        "and the problems you can solve for this employer."
    )
    assert data["projects_to_highlight"] == [
        "CareerMatch Assistant (matches FastAPI and PostgreSQL)"
    ]
    assert data["bullet_point_suggestions"] == [
        (
            "Add a CV bullet that connects Python, FastAPI, PostgreSQL, and Docker "
            "to a concrete result, such as a faster workflow, cleaner API, better "
            "reliability, or clearer reporting."
        ),
        (
            "Add or sharpen a project bullet for CareerMatch Assistant (matches "
            "FastAPI and PostgreSQL): explain the problem, your contribution, the "
            "tools used, and the outcome."
        ),
        (
            "Rewrite one experience bullet from your summary so it mirrors the "
            "Backend Developer responsibilities, while keeping the claim factual."
        ),
    ]
    assert data["missing_keyword_warnings"] == [
        (
            "The job mentions Azure, but this skill is not listed in the profile. "
            "Only add it to the CV if you have real experience with it."
        ),
        (
            "The job mentions Azure DevOps, but this skill is not listed in the profile. "
            "Only add it to the CV if you have real experience with it."
        ),
        (
            "The job mentions REST API, but this skill is not listed in the profile. "
            "Only add it to the CV if you have real experience with it."
        ),
    ]
    assert data["ethical_warning"] == (
        "Only include skills, projects, and experience you can honestly explain. "
        "Do not invent experience to match a job description."
    )


def test_cv_suggestions_can_use_fake_llm_provider(client: TestClient) -> None:
    app.dependency_overrides[get_llm_provider] = FakeLLMProvider
    profile_response = client.post(
        "/profiles",
        json={
            "target_roles": ["Backend Developer"],
            "skills": ["Python"],
            "projects": [{"name": "API Project", "skills": ["Python"]}],
        },
    )
    job_response = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "description": "Backend role requiring Python.",
        },
    )

    response = client.post(
        "/analysis/cv-suggestions",
        json={
            "profile_id": profile_response.json()["id"],
            "job_id": job_response.json()["id"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tailored_summary_suggestion"].startswith(
        "Fake LLM enhanced summary for Backend Developer at Example Co:"
    )
    assert data["bullet_point_suggestions"][0] == (
        "Fake LLM draft: turn one relevant project into a measurable, "
        "truthful achievement bullet."
    )
    assert data["ethical_warning"] == (
        "Only include skills, projects, and experience you can honestly explain. "
        "Do not invent experience to match a job description."
    )


def test_cv_suggestions_fall_back_when_llm_provider_fails(
    client: TestClient,
) -> None:
    app.dependency_overrides[get_llm_provider] = BrokenLLMProvider
    profile_response = client.post(
        "/profiles",
        json={"target_roles": ["Backend Developer"], "skills": ["Python"]},
    )
    job_response = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "description": "Backend role requiring Python.",
        },
    )

    response = client.post(
        "/analysis/cv-suggestions",
        json={
            "profile_id": profile_response.json()["id"],
            "job_id": job_response.json()["id"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tailored_summary_suggestion"].startswith(
        "Position your CV summary for the Backend Developer at Example Co role"
    )
    assert not data["tailored_summary_suggestion"].startswith("Fake LLM")


def test_cv_suggestions_return_404_for_missing_profile(client: TestClient) -> None:
    job_response = client.post(
        "/jobs",
        json={"title": "Backend Developer", "company": "Example Co"},
    )

    response = client.post(
        "/analysis/cv-suggestions",
        json={"profile_id": 999, "job_id": job_response.json()["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_cv_suggestions_return_404_for_missing_job(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={"target_roles": ["Backend Developer"], "skills": ["Python"]},
    )

    response = client.post(
        "/analysis/cv-suggestions",
        json={"profile_id": profile_response.json()["id"], "job_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_interview_prep_generates_questions_and_three_day_plan(
    client: TestClient,
) -> None:
    profile_response = client.post(
        "/profiles",
        json={
            "target_roles": ["Backend Developer"],
            "skills": ["Python", "FastAPI"],
            "projects": [
                {
                    "name": "CareerMatch Assistant",
                    "description": "FastAPI backend for job matching.",
                    "skills": ["Python", "FastAPI"],
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
                "Backend Developer role. Need Python, FastAPI, Docker, and "
                "REST API experience."
            ),
            "requirements": ["Python", "FastAPI", "Docker"],
            "seniority": "mid-level",
        },
    )

    response = client.post(
        "/analysis/interview-prep",
        json={
            "profile_id": profile_response.json()["id"],
            "job_id": job_response.json()["id"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["technical_questions"][:2] == [
        {
            "skill": "Python",
            "questions": [
                "How do you structure a Python service so it is easy to test and maintain?",
                "How would you debug a slow Python API endpoint?",
            ],
        },
        {
            "skill": "FastAPI",
            "questions": [
                "How do FastAPI dependencies help organize request handling?",
                "How would you validate request and response data in a FastAPI endpoint?",
            ],
        },
    ]
    assert {
        "skill": "Docker",
        "questions": [
            "How would you explain the difference between an image and a container?",
            "How would you debug a service that works locally but fails in Docker?",
        ],
    } in data["technical_questions"]
    assert data["hr_questions"][0] == (
        "Why are you interested in the Backend Developer role at Example Co?"
    )
    assert data["weak_areas"] == [
        "Docker is mentioned in the job but not listed in the profile.",
        "REST API is mentioned in the job but not listed in the profile.",
    ]
    assert data["study_topics"][:4] == [
        "Review the basics of Docker and prepare an honest gap explanation.",
        "Review the basics of REST API and prepare an honest gap explanation.",
        "Prepare a project example that demonstrates Python.",
        "Prepare a project example that demonstrates FastAPI.",
    ]
    assert data["three_day_plan"] == [
        {
            "day": 1,
            "focus": "Map the role to your real experience",
            "tasks": [
                "Reread the Backend Developer description and mark the top responsibilities.",
                "Prepare a 2-minute walkthrough of your most relevant project.",
                "Prepare examples for matched skills: Python and FastAPI.",
            ],
        },
        {
            "day": 2,
            "focus": "Practice technical and behavioral answers",
            "tasks": [
                "Practice technical questions for the required skills.",
                "Write short STAR-format notes for two project or teamwork stories.",
                "Study weak areas honestly: Docker and REST API.",
            ],
        },
        {
            "day": 3,
            "focus": "Mock interview and final polish",
            "tasks": [
                "Run a mock interview and answer questions out loud.",
                "Prepare thoughtful questions about Example Co, the team, and success metrics.",
                "Review the requirement summary and connect it to your examples.",
            ],
        },
    ]


def test_interview_prep_can_use_fake_llm_provider(client: TestClient) -> None:
    app.dependency_overrides[get_llm_provider] = FakeLLMProvider
    profile_response = client.post(
        "/profiles",
        json={"target_roles": ["Backend Developer"], "skills": ["Python"]},
    )
    job_response = client.post(
        "/jobs",
        json={
            "title": "Backend Developer",
            "company": "Example Co",
            "description": "Backend role requiring Python.",
        },
    )

    response = client.post(
        "/analysis/interview-prep",
        json={
            "profile_id": profile_response.json()["id"],
            "job_id": job_response.json()["id"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["technical_questions"][0] == {
        "skill": "Role-specific practice",
        "questions": [
            (
                "Fake LLM question: which project best proves you can do the "
                "Backend Developer role?"
            )
        ],
    }
    assert data["technical_questions"][1]["skill"] == "Python"


def test_interview_prep_returns_404_for_missing_profile(client: TestClient) -> None:
    job_response = client.post(
        "/jobs",
        json={"title": "Backend Developer", "company": "Example Co"},
    )

    response = client.post(
        "/analysis/interview-prep",
        json={"profile_id": 999, "job_id": job_response.json()["id"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_interview_prep_returns_404_for_missing_job(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={"target_roles": ["Backend Developer"], "skills": ["Python"]},
    )

    response = client.post(
        "/analysis/interview-prep",
        json={"profile_id": profile_response.json()["id"], "job_id": 999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_openapi_schema_includes_analysis_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/analysis/job" in response.json()["paths"]
    assert "/analysis/match" in response.json()["paths"]
    assert "/analysis/cv-suggestions" in response.json()["paths"]
    assert "/analysis/interview-prep" in response.json()["paths"]
