import re
from typing import Any

from app.models.job import Job
from app.models.profile import Profile
from app.services.job_analyzer import SKILL_PATTERNS, analyze_job_description


def match_profile_to_job(profile: Profile, job: Job) -> dict[str, object]:
    job_text = _job_text(job)
    job_analysis = analyze_job_description(job_text)
    job_skills = list(job_analysis["extracted_skills"])
    profile_skills = _canonicalize_skills(profile.skills)
    project_skills = _canonicalize_project_skills(profile.projects)

    matched_skills = [
        skill for skill in job_skills if _normalize_skill(skill) in profile_skills
    ]
    missing_skills = [
        skill for skill in job_skills if _normalize_skill(skill) not in profile_skills
    ]
    project_matches = [
        skill for skill in job_skills if _normalize_skill(skill) in project_skills
    ]

    skill_match_score = _ratio_score(len(matched_skills), len(job_skills), 60)
    target_role_score = _target_role_score(profile.target_roles, job_text)
    project_relevance_score = _ratio_score(len(project_matches), len(job_skills), 20)
    total_score = skill_match_score + target_role_score + project_relevance_score

    strengths = _build_strengths(
        matched_skills,
        profile.target_roles,
        job_text,
        project_matches,
    )
    gaps = _build_gaps(missing_skills, profile.target_roles, job_text, project_matches)

    return {
        "score": total_score,
        "score_breakdown": {
            "skill_match": skill_match_score,
            "target_role_match": target_role_score,
            "project_relevance": project_relevance_score,
        },
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "strengths": strengths,
        "gaps": gaps,
        "recommendation": _recommend(total_score),
    }


def _job_text(job: Job) -> str:
    parts = [
        job.title,
        job.seniority,
        job.description,
        " ".join(job.requirements or []),
    ]
    return " ".join(part for part in parts if part)


def _canonicalize_skills(skills: list[str]) -> set[str]:
    canonical_skills: set[str] = set()

    for raw_skill in skills:
        normalized_skill = _normalize_text(raw_skill)
        matched_known_skill = False

        for skill, patterns in SKILL_PATTERNS:
            if any(re.search(pattern, normalized_skill) for pattern in patterns):
                canonical_skills.add(_normalize_skill(skill))
                matched_known_skill = True

        if not matched_known_skill:
            canonical_skills.add(normalized_skill)

    return canonical_skills


def _canonicalize_project_skills(projects: list[dict[str, Any]]) -> set[str]:
    project_skills: list[str] = []
    for project in projects:
        skills = project.get("skills", [])
        if isinstance(skills, list):
            project_skills.extend(str(skill) for skill in skills)

    return _canonicalize_skills(project_skills)


def _target_role_score(target_roles: list[str], job_text: str) -> int:
    normalized_job_text = _normalize_text(job_text)
    if not target_roles:
        return 0

    for role in target_roles:
        normalized_role = _normalize_text(role)
        if normalized_role and normalized_role in normalized_job_text:
            return 20

    role_tokens = {
        token
        for role in target_roles
        for token in re.findall(r"[a-z0-9]+", _normalize_text(role))
        if len(token) >= 4
    }
    job_tokens = set(re.findall(r"[a-z0-9]+", normalized_job_text))
    if role_tokens & job_tokens:
        return 10

    return 0


def _ratio_score(matched_count: int, total_count: int, max_points: int) -> int:
    if total_count == 0:
        return 0
    return round((matched_count / total_count) * max_points)


def _build_strengths(
    matched_skills: list[str],
    target_roles: list[str],
    job_text: str,
    project_matches: list[str],
) -> list[str]:
    strengths: list[str] = []

    if matched_skills:
        strengths.append(f"Profile matches required skills: {', '.join(matched_skills)}.")

    matching_roles = [
        role
        for role in target_roles
        if _normalize_text(role) and _normalize_text(role) in _normalize_text(job_text)
    ]
    if matching_roles:
        strengths.append(f"Target role aligns with this job: {matching_roles[0]}.")

    if project_matches:
        strengths.append(
            "Profile projects show relevant experience with "
            f"{', '.join(project_matches)}."
        )

    if not strengths:
        strengths.append("No strong match signals were found yet.")

    return strengths


def _build_gaps(
    missing_skills: list[str],
    target_roles: list[str],
    job_text: str,
    project_matches: list[str],
) -> list[str]:
    gaps: list[str] = []

    if missing_skills:
        gaps.append(f"Job mentions skills not listed in the profile: {', '.join(missing_skills)}.")

    if target_roles and _target_role_score(target_roles, job_text) == 0:
        gaps.append("Job title and description do not clearly match the profile target roles.")

    if not project_matches:
        gaps.append("No profile project directly supports the extracted job skills.")

    if not gaps:
        gaps.append("No major gaps were found from the available profile and job data.")

    return gaps


def _recommend(score: int) -> str:
    if score >= 80:
        return "Strong match. This job is worth prioritizing."
    if score >= 60:
        return "Good match. Review the gaps before tailoring the CV."
    if score >= 40:
        return "Partial match. Apply only if the missing skills are acceptable or learnable."
    return "Weak match. This job may need significant upskilling or a different profile angle."


def _normalize_skill(skill: str) -> str:
    return _normalize_text(skill)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()
