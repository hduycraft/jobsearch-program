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


class CvSuggestionsRequest(BaseModel):
    profile_id: int
    job_id: int


class CvSuggestionsResponse(BaseModel):
    tailored_summary_suggestion: str
    projects_to_highlight: list[str]
    bullet_point_suggestions: list[str]
    missing_keyword_warnings: list[str]
    ethical_warning: str


class InterviewPrepRequest(BaseModel):
    profile_id: int
    job_id: int


class TechnicalQuestionGroup(BaseModel):
    skill: str
    questions: list[str]


class ThreeDayPlanItem(BaseModel):
    day: int
    focus: str
    tasks: list[str]


class InterviewPrepResponse(BaseModel):
    technical_questions: list[TechnicalQuestionGroup]
    hr_questions: list[str]
    study_topics: list[str]
    weak_areas: list[str]
    three_day_plan: list[ThreeDayPlanItem]
