from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


# ---- Auth Schemas ----
class RegisterRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    name: str = Field(..., min_length=2, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# ---- User Schemas ----
class UserResponse(BaseModel):
    id: UUID
    company_id: UUID
    email: str
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Company Schemas ----
class CompanyResponse(BaseModel):
    id: UUID
    name: str
    domain: Optional[str] = None
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Candidate Schemas ----
class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: float = 0
    current_status: str = "available"
    availability: str = "immediate"
    salary_expectation: Optional[float] = None
    salary_currency: str = "USD"
    location: Optional[str] = None
    open_to_remote: str = "false"
    notes: Optional[str] = None
    resume_text: Optional[str] = None
    seniority: Optional[str] = None
    industry: Optional[str] = None


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    current_status: Optional[str] = None
    availability: Optional[str] = None
    salary_expectation: Optional[float] = None
    location: Optional[str] = None
    open_to_remote: Optional[str] = None
    notes: Optional[str] = None
    resume_text: Optional[str] = None
    seniority: Optional[str] = None
    industry: Optional[str] = None


class CandidateResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: float = 0
    current_status: str = "available"
    last_interaction: Optional[datetime] = None
    previous_submissions: List[Dict[str, Any]] = []
    availability: str = "immediate"
    salary_expectation: Optional[float] = None
    salary_currency: str = "USD"
    location: Optional[str] = None
    open_to_remote: str = "false"
    notes: Optional[str] = None
    seniority: Optional[str] = None
    industry: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    candidates: List[CandidateResponse]
    total: int
    page: int
    per_page: int


# ---- Job Description Schemas ----
class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    raw_text: str = Field(..., min_length=10)


class JobDescriptionResponse(BaseModel):
    id: UUID
    company_id: UUID
    created_by: UUID
    title: str
    raw_text: str
    parsed_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobDescriptionListResponse(BaseModel):
    jobs: List[JobDescriptionResponse]
    total: int


class ParsedJDResponse(BaseModel):
    skills: Dict[str, List[str]]  # {"mandatory": [...], "optional": [...]}
    seniority: Optional[str] = None
    experience_range: Optional[Dict[str, float]] = None
    tools: List[str] = []
    industry: Optional[str] = None
    location: Optional[str] = None
    salary_band: Optional[Dict[str, Any]] = None
    domain: Optional[str] = None


# ---- Match Schemas ----
class MatchResponse(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    overall_score: float
    confidence: float
    skill_score: float
    experience_score: float
    seniority_score: float
    location_score: float
    compensation_score: float
    recency_score: float
    domain_score: float
    availability_score: float
    strengths: List[str] = []
    weaknesses: List[str] = []
    explanation: Dict[str, Any] = {}
    rediscovery_signals: List["RediscoverySignalResponse"] = []
    candidate: Optional[CandidateResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    matches: List[MatchResponse]
    total: int
    job_title: str


# ---- Rediscovery Signal Schemas ----
class RediscoverySignalResponse(BaseModel):
    id: UUID
    signal_type: str
    reason: str
    score_boost: float
    metadata: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Interaction Schemas ----
class InteractionCreate(BaseModel):
    candidate_id: UUID
    job_id: Optional[UUID] = None
    action: str  # contacted, pipelined, rejected, saved, exported, noted
    notes: Optional[str] = None


class InteractionResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    user_id: UUID
    job_id: Optional[UUID] = None
    action: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Analytics Schemas ----
class AnalyticsOverview(BaseModel):
    total_candidates: int
    total_jobs: int
    total_matches: int
    rediscovery_signals_count: int
    avg_match_score: float
    top_skills: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


class RediscoveryAnalytics(BaseModel):
    total_signals: int
    signals_by_type: Dict[str, int]
    top_rediscovered_candidates: List[Dict[str, Any]]
    rediscovery_rate: float


# ---- Search Schema ----
class SearchQuery(BaseModel):
    query: str = Field(..., min_length=3)


class SearchResult(BaseModel):
    candidates: List[CandidateResponse]
    interpretation: str
    filters_applied: Dict[str, Any]
