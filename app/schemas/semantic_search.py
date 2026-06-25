from pydantic import BaseModel, Field


class JobEmbeddingIndexItem(BaseModel):
    job_id: int
    content_hash: str
    vector_dimensions: int


class JobEmbeddingIndexResponse(BaseModel):
    indexed_count: int
    embeddings: list[JobEmbeddingIndexItem]


class SemanticJobSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=25)


class SemanticJobSearchResult(BaseModel):
    job_id: int
    title: str
    company: str
    similarity_score: float


class SemanticJobSearchResponse(BaseModel):
    query: str
    results: list[SemanticJobSearchResult]


class ProfileContextRequest(BaseModel):
    profile_id: int
    job_id: int
    limit: int = Field(default=3, ge=1, le=10)


class ProfileContextItem(BaseModel):
    item_type: str
    title: str
    similarity_score: float
    content: str
    skills: list[str] = Field(default_factory=list)


class ProfileContextResponse(BaseModel):
    profile_id: int
    job_id: int
    context_items: list[ProfileContextItem]
