from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    model: str


class RankedCandidate(BaseModel):
    filename: str
    candidate_name: Optional[str] = None
    compared_jd: Optional[str] = None
    score: float = Field(..., ge=0, le=100)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    extracted_skills: List[str] = Field(default_factory=list)
    top_keywords: List[str] = Field(default_factory=list)
    extracted_text_preview: str


class RankResponse(BaseModel):
    jd_preview: str
    total_files: int
    ranked_candidates: List[RankedCandidate]


class ErrorResponse(BaseModel):
    detail: str
