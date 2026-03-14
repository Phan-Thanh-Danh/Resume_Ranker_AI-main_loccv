from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    model: str


class RankedCandidate(BaseModel):
    filename: str = Field(..., description="Tên file CV")
    candidate_name: Optional[str] = Field(None, description="Tên ứng viên trích xuất được")
    compared_jd: Optional[str] = Field(None, description="JD được dùng để so sánh")
    score: float = Field(..., ge=0, le=100, description="Điểm phù hợp (0-100)")
    matched_skills: List[str] = Field(default_factory=list, description="Kỹ năng khớp với JD")
    missing_skills: List[str] = Field(default_factory=list, description="Kỹ năng còn thiếu so với JD")
    extracted_skills: List[str] = Field(default_factory=list, description="Toàn bộ kỹ năng trích xuất được")
    top_keywords: List[str] = Field(default_factory=list, description="Từ khóa quan trọng")
    extracted_text_preview: str = Field(..., description="Bản xem trước nội dung CV")


class RankResponse(BaseModel):
    jd_preview: str
    total_files: int
    ranked_candidates: List[RankedCandidate]


class ErrorResponse(BaseModel):
    detail: str
