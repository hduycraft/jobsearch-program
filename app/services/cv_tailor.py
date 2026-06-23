import re
from typing import Any

from app.models.job import Job
from app.models.profile import Profile
from app.services.job_analyzer import analyze_job_description
from app.services.llm_provider import LLMProvider
from app.services.matcher import match_profile_to_job

ETHICAL_WARNING = (
    "Only include skills, projects, and experience you can honestly explain. "
    "Do not invent experience to match a job description."
)


def build_cv_suggestions(
    profile: Profile,
    job: Job,
    llm_provider: LLMProvider | None = None,
) -> dict[str, object]:
    job_text = _job_text(job)
    job_analysis = analyze_job_description(job_text)
    job_skills = list(job_analysis["extracted_skills"])
    match_result = match_profile_to_job(profile, job)
    matched_skills = list(match_result["matched_skills"])
    missing_skills = list(match_result["missing_skills"])
    projects_to_highlight = _projects_to_highlight(profile.projects, job_skills)

    rule_based_suggestions = {
        "tailored_summary_suggestion": _summary_suggestion(
            profile=profile,
            job=job,
            matched_skills=matched_skills,
            projects_to_highlight=projects_to_highlight,
        ),
        "projects_to_highlight": projects_to_highlight,
        "bullet_point_suggestions": _bullet_point_suggestions(
            profile=profile,
            job=job,
            matched_skills=matched_skills,
            projects_to_highlight=projects_to_highlight,
        ),
        "missing_keyword_warnings": _missing_keyword_warnings(missing_skills),
        "ethical_warning": ETHICAL_WARNING,
    }
    return _with_llm_cv_enhancement(profile, job, rule_based_suggestions, llm_provider)


def _with_llm_cv_enhancement(
    profile: Profile,
    job: Job,
    rule_based_suggestions: dict[str, object],
    llm_provider: LLMProvider | None,
) -> dict[str, object]:
    if llm_provider is None:
        return rule_based_suggestions

    try:
        enhanced = llm_provider.enhance_cv_suggestions(
            profile=profile,
            job=job,
            rule_based_suggestions=rule_based_suggestions,
        )
    except Exception:
        return rule_based_suggestions

    if not enhanced or not rule_based_suggestions.keys() <= enhanced.keys():
        return rule_based_suggestions

    return enhanced


def _job_text(job: Job) -> str:
    parts = [
        job.title,
        job.seniority,
        job.description,
        " ".join(job.requirements or []),
    ]
    return " ".join(part for part in parts if part)


def _summary_suggestion(
    profile: Profile,
    job: Job,
    matched_skills: list[str],
    projects_to_highlight: list[str],
) -> str:
    role_context = f"{job.title} at {job.company}"

    if matched_skills:
        skill_clause = f"your experience with {_format_list(matched_skills)}"
    else:
        skill_clause = "your most relevant transferable experience"

    if projects_to_highlight:
        evidence_clause = f"using {_format_list(projects_to_highlight)} as evidence"
    elif profile.experience_summary:
        evidence_clause = "using your experience summary as evidence"
    else:
        evidence_clause = "using concrete examples from your real work"

    return (
        f"Position your CV summary for the {role_context} role by emphasizing "
        f"{skill_clause}, {evidence_clause}, and the problems you can solve for this employer."
    )


def _projects_to_highlight(
    projects: list[dict[str, Any]],
    job_skills: list[str],
) -> list[str]:
    highlighted_projects: list[str] = []
    normalized_job_skills = {_normalize_text(skill): skill for skill in job_skills}

    for project in projects:
        project_name = str(project.get("name", "")).strip()
        if not project_name:
            continue

        project_text = _project_text(project)
        matching_skills = [
            display_skill
            for normalized_skill, display_skill in normalized_job_skills.items()
            if normalized_skill in project_text
        ]

        if matching_skills:
            highlighted_projects.append(
                f"{project_name} (matches {_format_list(matching_skills)})"
            )

    return highlighted_projects[:3]


def _bullet_point_suggestions(
    profile: Profile,
    job: Job,
    matched_skills: list[str],
    projects_to_highlight: list[str],
) -> list[str]:
    bullets: list[str] = []

    if matched_skills:
        bullets.append(
            "Add a CV bullet that connects "
            f"{_format_list(matched_skills)} to a concrete result, such as a faster "
            "workflow, cleaner API, better reliability, or clearer reporting."
        )

    for project in projects_to_highlight:
        bullets.append(
            f"Add or sharpen a project bullet for {project}: explain the problem, "
            "your contribution, the tools used, and the outcome."
        )

    if profile.experience_summary:
        bullets.append(
            "Rewrite one experience bullet from your summary so it mirrors the "
            f"{job.title} responsibilities, while keeping the claim factual."
        )

    if not bullets:
        bullets.append(
            "Add one factual bullet that shows your closest relevant experience for "
            f"the {job.title} role, even if it uses adjacent skills rather than exact keywords."
        )

    return bullets[:5]


def _missing_keyword_warnings(missing_skills: list[str]) -> list[str]:
    if not missing_skills:
        return ["No missing job keywords were found from the known skill list."]

    return [
        (
            f"The job mentions {skill}, but this skill is not listed in the profile. "
            "Only add it to the CV if you have real experience with it."
        )
        for skill in missing_skills
    ]


def _project_text(project: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("name", "description"):
        value = project.get(key)
        if isinstance(value, str):
            parts.append(value)

    skills = project.get("skills", [])
    if isinstance(skills, list):
        parts.extend(str(skill) for skill in skills)

    return _normalize_text(" ".join(parts))


def _format_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()
