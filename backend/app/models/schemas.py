from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    links: Dict[str, str] = Field(default_factory=dict)

class EducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    details: List[str] = Field(default_factory=list)

class ExperienceItem(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

class ProjectItem(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    links: Dict[str, str] = Field(default_factory=dict)

class SkillSet(BaseModel):
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

class ProfileChunk(BaseModel):
    chunk_id: str
    source_type: Literal["experience", "project", "skill", "education", "summary"]
    source_ref: str
    text: str
    embedding_id: Optional[str] = None

class ResumeProfile(BaseModel):
    profile_id: str
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    skills: SkillSet = Field(default_factory=SkillSet)
    raw_hash: Optional[str] = None
    chunks: List[ProfileChunk] = Field(default_factory=list)

class ResumeUploadResponse(BaseModel):
    session_id: str
    profile_id: str
    status: str
    expires_at: datetime

class JobPosting(BaseModel):
    job_id: str
    source: str
    source_url: str
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    description: Optional[str] = None
    requirements: List[str] = Field(default_factory=list)
    nice_to_have: List[str] = Field(default_factory=list)
    salary_range: Optional[str] = None
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    hash: str

class MatchExplanation(BaseModel):
    job_id: str
    score: int = Field(ge=0, le=100)
    reasons: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)

class MatchResult(BaseModel):
    job_id: str
    job: JobPosting
    explanation: Optional[MatchExplanation] = None
    retrieval_score: float = 0.0
    rerank_score: float = 0.0
    final_score: float = 0.0
    explain_source: Literal["rules", "hybrid", "llm"] = "hybrid"

class TrackerItem(BaseModel):
    tracker_id: str
    profile_id: str
    job_id: str
    company: Optional[str] = None
    role: Optional[str] = None
    link: Optional[str] = None
    match_score: float = 0.0
    status: Literal["saved", "applied", "interview", "rejected", "offer", "archived"] = "saved"
    date_saved: datetime = Field(default_factory=datetime.utcnow)
    date_updated: datetime = Field(default_factory=datetime.utcnow)
    resume_version_id: Optional[str] = None
    notes: Optional[str] = None
