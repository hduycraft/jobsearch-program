from abc import ABC, abstractmethod
import json
from typing import TYPE_CHECKING

import httpx

from app.core.config import Settings, get_settings

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.profile import Profile


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def enhance_cv_suggestions(
        self,
        profile: "Profile",
        job: "Job",
        rule_based_suggestions: dict[str, object],
    ) -> dict[str, object] | None:
        raise NotImplementedError

    @abstractmethod
    def enhance_interview_prep(
        self,
        profile: "Profile",
        job: "Job",
        rule_based_prep: dict[str, object],
    ) -> dict[str, object] | None:
        raise NotImplementedError

    @abstractmethod
    def draft_cover_letter(self, profile: "Profile", job: "Job") -> str | None:
        raise NotImplementedError

    @abstractmethod
    def summarize_job(self, job: "Job") -> str | None:
        raise NotImplementedError


class NoLLMProvider(LLMProvider):
    name = "none"

    def enhance_cv_suggestions(
        self,
        profile: "Profile",
        job: "Job",
        rule_based_suggestions: dict[str, object],
    ) -> dict[str, object] | None:
        return None

    def enhance_interview_prep(
        self,
        profile: "Profile",
        job: "Job",
        rule_based_prep: dict[str, object],
    ) -> dict[str, object] | None:
        return None

    def draft_cover_letter(self, profile: "Profile", job: "Job") -> str | None:
        return None

    def summarize_job(self, job: "Job") -> str | None:
        return None


class FakeLLMProvider(LLMProvider):
    name = "fake"

    def enhance_cv_suggestions(
        self,
        profile: "Profile",
        job: "Job",
        rule_based_suggestions: dict[str, object],
    ) -> dict[str, object] | None:
        enhanced = dict(rule_based_suggestions)
        enhanced["tailored_summary_suggestion"] = (
            f"Fake LLM enhanced summary for {job.title} at {job.company}: "
            f"{rule_based_suggestions['tailored_summary_suggestion']}"
        )
        enhanced["bullet_point_suggestions"] = [
            (
                "Fake LLM draft: turn one relevant project into a measurable, "
                "truthful achievement bullet."
            ),
            *list(rule_based_suggestions["bullet_point_suggestions"]),
        ][:5]
        return enhanced

    def enhance_interview_prep(
        self,
        profile: "Profile",
        job: "Job",
        rule_based_prep: dict[str, object],
    ) -> dict[str, object] | None:
        enhanced = dict(rule_based_prep)
        enhanced["technical_questions"] = [
            {
                "skill": "Role-specific practice",
                "questions": [
                    (
                        f"Fake LLM question: which project best proves you can do "
                        f"the {job.title} role?"
                    )
                ],
            },
            *list(rule_based_prep["technical_questions"]),
        ]
        return enhanced

    def draft_cover_letter(self, profile: "Profile", job: "Job") -> str | None:
        return (
            f"Fake LLM cover letter draft for {job.title} at {job.company}. "
            "Review and edit before using."
        )

    def summarize_job(self, job: "Job") -> str | None:
        return f"Fake LLM job summary for {job.title} at {job.company}."


class OllamaLLMProvider(LLMProvider):
    name = "ollama"

    def __init__(
        self,
        model: str,
        base_url: str,
        timeout_seconds: float,
        client: httpx.Client | None = None,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.client = client

    def enhance_cv_suggestions(
        self,
        profile: "Profile",
        job: "Job",
        rule_based_suggestions: dict[str, object],
    ) -> dict[str, object] | None:
        summary = self._generate(
            prompt=(
                "Rewrite this CV summary suggestion so it is concise, specific, "
                "and honest. Do not invent skills, employers, metrics, or experience.\n\n"
                f"Profile:\n{_profile_context(profile)}\n\n"
                f"Job:\n{_job_context(job)}\n\n"
                "Rule-based suggestion:\n"
                f"{rule_based_suggestions['tailored_summary_suggestion']}"
            )
        )
        bullet = self._generate(
            prompt=(
                "Create one truthful CV bullet suggestion for this candidate and job. "
                "Keep it as a suggestion, not a fabricated final claim. "
                "Do not invent metrics or experience.\n\n"
                f"Profile:\n{_profile_context(profile)}\n\n"
                f"Job:\n{_job_context(job)}\n\n"
                "Existing bullet suggestions:\n"
                f"{_json_text(rule_based_suggestions['bullet_point_suggestions'])}"
            )
        )

        if summary is None and bullet is None:
            return None

        enhanced = dict(rule_based_suggestions)
        if summary:
            enhanced["tailored_summary_suggestion"] = summary
        if bullet:
            enhanced["bullet_point_suggestions"] = [
                bullet,
                *list(rule_based_suggestions["bullet_point_suggestions"]),
            ][:5]
        return enhanced

    def enhance_interview_prep(
        self,
        profile: "Profile",
        job: "Job",
        rule_based_prep: dict[str, object],
    ) -> dict[str, object] | None:
        question = self._generate(
            prompt=(
                "Create one practical interview question tailored to this candidate "
                "and job. The question should help the candidate prepare honestly.\n\n"
                f"Profile:\n{_profile_context(profile)}\n\n"
                f"Job:\n{_job_context(job)}\n\n"
                "Existing interview prep:\n"
                f"{_json_text(rule_based_prep)}"
            )
        )

        if question is None:
            return None

        enhanced = dict(rule_based_prep)
        enhanced["technical_questions"] = [
            {
                "skill": "Ollama-generated practice",
                "questions": [question],
            },
            *list(rule_based_prep["technical_questions"]),
        ]
        return enhanced

    def draft_cover_letter(self, profile: "Profile", job: "Job") -> str | None:
        return self._generate(
            prompt=(
                "Draft a short cover letter for this candidate and job. "
                "Keep it honest, concrete, and easy for the user to edit. "
                "Do not invent experience.\n\n"
                f"Profile:\n{_profile_context(profile)}\n\n"
                f"Job:\n{_job_context(job)}"
            )
        )

    def summarize_job(self, job: "Job") -> str | None:
        return self._generate(
            prompt=(
                "Summarize this job in 3 short bullets: role focus, key skills, "
                "and preparation priority.\n\n"
                f"Job:\n{_job_context(job)}"
            )
        )

    def _generate(self, prompt: str) -> str | None:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }

        try:
            if self.client is not None:
                response = self.client.post("/api/generate", json=payload)
            else:
                with httpx.Client(
                    base_url=self.base_url,
                    timeout=self.timeout_seconds,
                ) as client:
                    response = client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError):
            return None

        generated_text = data.get("response")
        if not isinstance(generated_text, str):
            return None

        generated_text = generated_text.strip()
        return generated_text or None


def build_llm_provider(settings: Settings) -> LLMProvider:
    provider_name = settings.llm_provider.strip().casefold()

    if provider_name == "fake":
        return FakeLLMProvider()

    if provider_name == "ollama":
        return OllamaLLMProvider(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    return NoLLMProvider()


def get_llm_provider() -> LLMProvider:
    return build_llm_provider(get_settings())


def _profile_context(profile: "Profile") -> str:
    return _json_text(
        {
            "target_roles": profile.target_roles,
            "skills": profile.skills,
            "experience_summary": profile.experience_summary,
            "projects": profile.projects,
        }
    )


def _job_context(job: "Job") -> str:
    return _json_text(
        {
            "title": job.title,
            "company": job.company,
            "seniority": job.seniority,
            "description": job.description,
            "requirements": job.requirements,
        }
    )


def _json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, default=str)
