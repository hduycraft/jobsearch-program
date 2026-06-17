from pydantic import BaseModel, Field


class JobAnalysisRequest(BaseModel):
    description: str = Field(..., min_length=1)


class JobAnalysisResponse(BaseModel):
    extracted_skills: list[str]
    seniority_estimate: str | None
    requirements_summary: list[str]


class MatchRequest(BaseModel):
    profile_id: int
    job_id: int


class MatchScoreBreakdown(BaseModel):
    skill_match: int
    target_role_match: int
    project_relevance: int


class MatchResponse(BaseModel):
    score: int
    score_breakdown: MatchScoreBreakdown
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    gaps: list[str]
    recommendation: str
