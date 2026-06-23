from dataclasses import dataclass
from typing import Protocol, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.job import Job as JobModel
from app.schemas.imports import ImportJobItem, ManualJobImportRequest, SkippedImportJob


class JobSourceAdapter(Protocol):
    def fetch_jobs(self) -> Sequence[ImportJobItem]:
        pass


@dataclass(frozen=True)
class ProvidedJobsAdapter:
    jobs: Sequence[ImportJobItem]

    def fetch_jobs(self) -> Sequence[ImportJobItem]:
        return self.jobs


@dataclass(frozen=True)
class JobImportSource:
    name: str
    adapter: JobSourceAdapter


@dataclass(frozen=True)
class JobImportResult:
    source_name: str
    imported_jobs: list[JobModel]
    skipped_jobs: list[SkippedImportJob]


def build_manual_jobs_source(request: ManualJobImportRequest) -> JobImportSource:
    return JobImportSource(
        name=_clean_text(request.source_name) or "manual",
        adapter=ProvidedJobsAdapter(request.jobs),
    )


def import_jobs(db: Session, source: JobImportSource) -> JobImportResult:
    imported_jobs: list[JobModel] = []
    skipped_jobs: list[SkippedImportJob] = []
    seen_keys: set[tuple[str, str, str | None]] = set()

    for raw_job in source.adapter.fetch_jobs():
        normalized_job = _normalize_job(raw_job)
        duplicate_key = _dedupe_key(normalized_job)

        if duplicate_key in seen_keys or _job_exists(db, normalized_job):
            skipped_jobs.append(_skipped_job(normalized_job, "duplicate"))
            continue

        job = JobModel(
            title=normalized_job.title,
            company=normalized_job.company,
            location=normalized_job.location,
            source=source.name,
            source_url=normalized_job.source_url,
            description=normalized_job.description,
            requirements=normalized_job.requirements,
            seniority=normalized_job.seniority,
        )
        db.add(job)
        imported_jobs.append(job)
        seen_keys.add(duplicate_key)

    db.commit()
    for job in imported_jobs:
        db.refresh(job)

    return JobImportResult(
        source_name=source.name,
        imported_jobs=imported_jobs,
        skipped_jobs=skipped_jobs,
    )


def _normalize_job(job: ImportJobItem) -> ImportJobItem:
    return ImportJobItem(
        title=_clean_text(job.title),
        company=_clean_text(job.company),
        location=_clean_optional_text(job.location),
        source_url=_clean_optional_text(job.source_url),
        description=_clean_optional_text(job.description),
        requirements=_clean_requirements(job.requirements),
        seniority=_clean_optional_text(job.seniority),
    )


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned_value = _clean_text(value)
    return cleaned_value or None


def _clean_requirements(requirements: Sequence[str]) -> list[str]:
    cleaned_requirements: list[str] = []
    seen_requirements: set[str] = set()

    for requirement in requirements:
        cleaned_requirement = _clean_text(requirement)
        normalized_requirement = _normalize_for_match(cleaned_requirement)

        if not cleaned_requirement or normalized_requirement in seen_requirements:
            continue

        cleaned_requirements.append(cleaned_requirement)
        seen_requirements.add(normalized_requirement)

    return cleaned_requirements


def _job_exists(db: Session, job: ImportJobItem) -> bool:
    query = select(JobModel.id).where(
        or_(
            JobModel.source_url == job.source_url if job.source_url else False,
            (
                (func.lower(JobModel.title) == job.title.lower())
                & (func.lower(JobModel.company) == job.company.lower())
            ),
        )
    )
    return db.scalar(query) is not None


def _dedupe_key(job: ImportJobItem) -> tuple[str, str, str | None]:
    return (
        _normalize_for_match(job.title),
        _normalize_for_match(job.company),
        _normalize_for_match(job.source_url) if job.source_url else None,
    )


def _skipped_job(job: ImportJobItem, reason: str) -> SkippedImportJob:
    return SkippedImportJob(
        title=job.title,
        company=job.company,
        source_url=job.source_url,
        reason=reason,
    )


def _normalize_for_match(value: str | None) -> str:
    if value is None:
        return ""

    return _clean_text(value).lower()
