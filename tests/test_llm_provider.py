import json

import httpx

from app.core.config import Settings
from app.models.job import Job
from app.models.profile import Profile
from app.services.llm_provider import (
    FakeLLMProvider,
    NoLLMProvider,
    OllamaLLMProvider,
    build_llm_provider,
)


def test_build_llm_provider_defaults_to_no_provider() -> None:
    provider = build_llm_provider(Settings(llm_provider="none"))

    assert isinstance(provider, NoLLMProvider)
    assert provider.name == "none"


def test_build_llm_provider_can_select_fake_provider() -> None:
    provider = build_llm_provider(Settings(llm_provider="fake"))

    assert isinstance(provider, FakeLLMProvider)
    assert provider.name == "fake"


def test_build_llm_provider_can_select_ollama_provider() -> None:
    provider = build_llm_provider(
        Settings(
            llm_provider="ollama",
            llm_model="llama3.2:3b",
            ollama_base_url="http://localhost:11434",
        )
    )

    assert isinstance(provider, OllamaLLMProvider)
    assert provider.name == "ollama"
    assert provider.model == "llama3.2:3b"
    assert provider.base_url == "http://localhost:11434"


def test_build_llm_provider_falls_back_for_unknown_provider() -> None:
    provider = build_llm_provider(Settings(llm_provider="unknown"))

    assert isinstance(provider, NoLLMProvider)


def test_ollama_provider_sends_generate_request() -> None:
    requests: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"response": "Use FastAPI experience."})

    client = httpx.Client(
        base_url="http://testserver",
        transport=httpx.MockTransport(handler),
    )
    provider = OllamaLLMProvider(
        model="llama3.2:3b",
        base_url="http://testserver",
        timeout_seconds=20,
        client=client,
    )

    summary = provider.summarize_job(
        Job(title="Backend Developer", company="Example Co")
    )

    assert summary == "Use FastAPI experience."
    assert requests[0]["model"] == "llama3.2:3b"
    assert requests[0]["stream"] is False
    assert "Summarize this job" in str(requests[0]["prompt"])


def test_ollama_provider_enhances_cv_suggestions() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        prompt = str(json.loads(request.content)["prompt"])
        if "Rewrite this CV summary" in prompt:
            return httpx.Response(200, json={"response": "Lead with API delivery."})
        return httpx.Response(
            200,
            json={"response": "Suggest adding one truthful FastAPI project bullet."},
        )

    client = httpx.Client(
        base_url="http://testserver",
        transport=httpx.MockTransport(handler),
    )
    provider = OllamaLLMProvider(
        model="llama3.2:3b",
        base_url="http://testserver",
        timeout_seconds=20,
        client=client,
    )

    enhanced = provider.enhance_cv_suggestions(
        profile=Profile(
            target_roles=["Backend Developer"],
            skills=["Python", "FastAPI"],
            projects=[{"name": "CareerMatch", "skills": ["FastAPI"]}],
        ),
        job=Job(title="Backend Developer", company="Example Co"),
        rule_based_suggestions={
            "tailored_summary_suggestion": "Rule-based summary.",
            "projects_to_highlight": ["CareerMatch"],
            "bullet_point_suggestions": ["Rule-based bullet."],
            "missing_keyword_warnings": [],
            "ethical_warning": "Do not invent experience.",
        },
    )

    assert enhanced is not None
    assert enhanced["tailored_summary_suggestion"] == "Lead with API delivery."
    assert enhanced["bullet_point_suggestions"] == [
        "Suggest adding one truthful FastAPI project bullet.",
        "Rule-based bullet.",
    ]


def test_ollama_provider_returns_none_when_ollama_fails() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "model not found"})

    client = httpx.Client(
        base_url="http://testserver",
        transport=httpx.MockTransport(handler),
    )
    provider = OllamaLLMProvider(
        model="missing-model",
        base_url="http://testserver",
        timeout_seconds=20,
        client=client,
    )

    summary = provider.summarize_job(
        Job(title="Backend Developer", company="Example Co")
    )

    assert summary is None
