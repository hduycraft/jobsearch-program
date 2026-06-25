import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_embedding import JobEmbedding
from app.models.profile import Profile

VECTOR_DIMENSIONS = 64
TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9+#.]*")

STOP_WORDS = {
    "a",
    "and",
    "are",
    "as",
    "at",
    "be",
    "for",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


@dataclass(frozen=True)
class IndexedJobEmbedding:
    job_id: int
    content_hash: str
    vector_dimensions: int


@dataclass(frozen=True)
class JobSearchResult:
    job_id: int
    title: str
    company: str
    similarity_score: float


@dataclass(frozen=True)
class ProfileContextResult:
    item_type: str
    title: str
    similarity_score: float
    content: str
    skills: list[str]


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(text.lower())
        if token not in STOP_WORDS
    ]


def embed_text(text: str) -> list[float]:
    vector = [0.0] * VECTOR_DIMENSIONS
    for token in tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % VECTOR_DIMENSIONS
        vector[index] += 1.0

    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector

    return [round(value / magnitude, 6) for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    score = sum(left_value * right_value for left_value, right_value in zip(left, right))
    return round(score, 4)


def build_job_embedding_text(job: Job) -> str:
    text_parts = [
        job.title,
        job.company,
        job.location or "",
        job.seniority or "",
        job.description or "",
        " ".join(job.requirements or []),
    ]
    return " ".join(part for part in text_parts if part)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def index_job_embeddings(db: Session) -> list[IndexedJobEmbedding]:
    jobs = list(db.scalars(select(Job).order_by(Job.id)))
    indexed: list[IndexedJobEmbedding] = []

    for job in jobs:
        embedding_text = build_job_embedding_text(job)
        new_hash = content_hash(embedding_text)
        existing = db.scalar(
            select(JobEmbedding).where(JobEmbedding.job_id == job.id)
        )

        if existing is None:
            existing = JobEmbedding(
                job_id=job.id,
                content_hash=new_hash,
                embedding=embed_text(embedding_text),
            )
            db.add(existing)
        elif existing.content_hash != new_hash:
            existing.content_hash = new_hash
            existing.embedding = embed_text(embedding_text)

        indexed.append(
            IndexedJobEmbedding(
                job_id=job.id,
                content_hash=new_hash,
                vector_dimensions=VECTOR_DIMENSIONS,
            )
        )

    db.commit()
    return indexed


def search_indexed_jobs(
    db: Session,
    query: str,
    limit: int,
) -> list[JobSearchResult]:
    query_embedding = embed_text(query)
    stored_embeddings = list(
        db.scalars(select(JobEmbedding).join(Job).order_by(Job.id))
    )

    results = [
        JobSearchResult(
            job_id=stored_embedding.job.id,
            title=stored_embedding.job.title,
            company=stored_embedding.job.company,
            similarity_score=cosine_similarity(
                query_embedding,
                stored_embedding.embedding,
            ),
        )
        for stored_embedding in stored_embeddings
    ]
    results.sort(key=lambda result: (-result.similarity_score, result.job_id))
    return results[:limit]


def retrieve_profile_context(
    profile: Profile,
    job: Job,
    limit: int,
) -> list[ProfileContextResult]:
    query_embedding = embed_text(build_job_embedding_text(job))
    candidates: list[ProfileContextResult] = []

    if profile.experience_summary:
        candidates.append(
            _score_context_item(
                query_embedding=query_embedding,
                item_type="experience_summary",
                title="Experience summary",
                content=profile.experience_summary,
                skills=[],
            )
        )

    for project in profile.projects or []:
        project_name = _string_from_project(project, "name") or "Untitled project"
        project_description = _string_from_project(project, "description")
        project_skills = _skills_from_project(project)
        content = " ".join(
            part
            for part in [
                project_name,
                project_description,
                " ".join(project_skills),
            ]
            if part
        )
        candidates.append(
            _score_context_item(
                query_embedding=query_embedding,
                item_type="project",
                title=project_name,
                content=content,
                skills=project_skills,
            )
        )

    candidates.sort(key=lambda item: (-item.similarity_score, item.title))
    return candidates[:limit]


def _score_context_item(
    query_embedding: list[float],
    item_type: str,
    title: str,
    content: str,
    skills: list[str],
) -> ProfileContextResult:
    return ProfileContextResult(
        item_type=item_type,
        title=title,
        similarity_score=cosine_similarity(query_embedding, embed_text(content)),
        content=content,
        skills=skills,
    )


def _string_from_project(project: Any, key: str) -> str | None:
    if not isinstance(project, dict):
        return None

    value = project.get(key)
    if isinstance(value, str):
        return value
    return None


def _skills_from_project(project: Any) -> list[str]:
    if not isinstance(project, dict):
        return []

    skills = project.get("skills", [])
    if not isinstance(skills, list):
        return []

    return [skill for skill in skills if isinstance(skill, str)]
