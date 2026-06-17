import re


SKILL_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Python", (r"\bpython\b",)),
    ("FastAPI", (r"\bfastapi\b", r"\bfast api\b")),
    ("SQL", (r"\bsql\b",)),
    ("PostgreSQL", (r"\bpostgresql\b", r"\bpostgres\b")),
    ("Docker", (r"\bdocker\b",)),
    ("Azure", (r"\bazure\b",)),
    ("Azure DevOps", (r"\bazure\s+devops\b",)),
    ("Git", (r"\bgit\b", r"\bgithub\b", r"\bgitlab\b")),
    ("REST API", (r"\brest\s+apis?\b", r"\brestful\s+apis?\b")),
    ("Machine Learning", (r"\bmachine\s+learning\b", r"\bml\b")),
    ("NLP", (r"\bnlp\b", r"\bnatural\s+language\s+processing\b")),
    ("RAG", (r"\brag\b", r"\bretrieval[-\s]+augmented\s+generation\b")),
    ("LLM", (r"\bllms?\b", r"\blarge\s+language\s+models?\b")),
    ("React", (r"\breact\b", r"\breact\.js\b", r"\breactjs\b")),
    ("Next.js", (r"\bnext\.?js\b",)),
)

SENIORITY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("lead", (r"\blead\b", r"\bstaff\b", r"\bprincipal\b")),
    ("senior", (r"\bsenior\b", r"\bsr\.?\b")),
    ("mid-level", (r"\bmid[-\s]?level\b", r"\bintermediate\b")),
    ("junior", (r"\bjunior\b", r"\bjr\.?\b", r"\bentry[-\s]?level\b")),
    ("intern", (r"\bintern\b", r"\binternship\b")),
)

REQUIREMENT_KEYWORDS: tuple[str, ...] = (
    "required",
    "requirement",
    "must",
    "should",
    "need",
    "needs",
    "looking for",
    "experience",
    "proficient",
    "familiar",
    "knowledge",
    "responsible",
    "build",
    "design",
    "develop",
    "maintain",
    "work with",
    "hands-on",
)


def analyze_job_description(description: str) -> dict[str, object]:
    normalized_description = _normalize_text(description)
    extracted_skills = extract_skills(normalized_description)

    return {
        "extracted_skills": extracted_skills,
        "seniority_estimate": estimate_seniority(normalized_description),
        "requirements_summary": summarize_requirements(
            description,
            extracted_skills,
        ),
    }


def extract_skills(text: str) -> list[str]:
    found_skills: list[str] = []

    for skill, patterns in SKILL_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            found_skills.append(skill)

    return found_skills


def estimate_seniority(text: str) -> str | None:
    for seniority, patterns in SENIORITY_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            return seniority

    years = [int(match) for match in re.findall(r"\b(\d{1,2})\+?\s+years?\b", text)]
    if not years:
        return None

    max_years = max(years)
    if max_years >= 5:
        return "senior"
    if max_years >= 2:
        return "mid-level"
    return "junior"


def summarize_requirements(description: str, extracted_skills: list[str]) -> list[str]:
    candidates = _split_requirement_candidates(description)
    requirements: list[str] = []
    seen: set[str] = set()

    for candidate in candidates:
        normalized_candidate = _normalize_text(candidate)
        if not normalized_candidate:
            continue

        mentions_requirement = any(
            keyword in normalized_candidate for keyword in REQUIREMENT_KEYWORDS
        )
        mentions_skill = any(
            re.search(pattern, normalized_candidate)
            for skill, patterns in SKILL_PATTERNS
            if skill in extracted_skills
            for pattern in patterns
        )

        if not mentions_requirement and not mentions_skill:
            continue

        cleaned_candidate = _clean_requirement(candidate)
        dedupe_key = cleaned_candidate.casefold()
        if cleaned_candidate and dedupe_key not in seen:
            requirements.append(cleaned_candidate)
            seen.add(dedupe_key)

    if requirements:
        return requirements[:8]

    fallback = _clean_requirement(description)
    return [fallback] if fallback else []


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def _split_requirement_candidates(description: str) -> list[str]:
    line_parts = re.split(r"[\r\n]+", description)
    candidates: list[str] = []

    for line in line_parts:
        cleaned_line = _clean_requirement(line)
        if not cleaned_line:
            continue
        candidates.extend(
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", cleaned_line)
            if part.strip()
        )

    return candidates


def _clean_requirement(text: str) -> str:
    cleaned_text = re.sub(r"^\s*(?:[-*]|\u2022|\d+[.)])\s*", "", text).strip()
    return re.sub(r"\s+", " ", cleaned_text)
