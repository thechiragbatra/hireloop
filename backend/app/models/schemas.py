from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class Contact(BaseModel):
    """Contact information (kept minimal)."""

    email: str | None = Field(default=None, description="Contact email")
    phone: str | None = Field(default=None, description="Contact phone")
    location: str | None = Field(default=None, description="Location")
    linkedin: str | None = Field(default=None, description="LinkedIn URL")
    github: str | None = Field(default=None, description="GitHub URL")
    website: str | None = Field(default=None, description="Website URL")


class Bullet(BaseModel):
    """A resume bullet with stable id for source citation."""

    id: str = Field(description="Stable identifier for citation")
    text: str = Field(description="Bullet text")


class ExperienceItem(BaseModel):
    """Work experience entry."""

    id: str = Field(description="Stable identifier")
    company: str = Field(description="Company name")
    title: str = Field(description="Job title")
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    location: str | None = Field(default=None)
    bullets: list[Bullet] = Field(default_factory=list)


class EducationItem(BaseModel):
    """Education entry."""

    id: str = Field(description="Stable identifier")
    institution: str = Field(description="Institution name")
    degree: str | None = Field(default=None)
    field_of_study: str | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)


class ProjectItem(BaseModel):
    """Project entry with bullets and stable ids."""

    id: str = Field(description="Stable identifier")
    name: str = Field(description="Project name")
    description: str | None = Field(default=None)
    bullets: list[Bullet] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    url: str | None = Field(default=None)


class Profile(BaseModel):
    """User profile schema with stable ids for source citations."""

    id: str = Field(description="Profile identifier")
    contact: Contact | None = Field(default=None)
    skills: list[str] = Field(default_factory=list, description="Skills list")
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)


class Job(BaseModel):
    """Job posting schema."""

    id: str = Field(description="Job identifier")
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    location: str | None = Field(default=None)
    description: str = Field(description="Job description")
    requirements: list[str] = Field(default_factory=list)
    url: str | None = Field(default=None)
    source: str = Field(description="Source: greenhouse|lever|ashby|adzuna|remoteok|custom")


class MatchResult(BaseModel):
    """Match result with explanation."""

    job_id: str = Field(description="Job identifier")
    score: float = Field(ge=0, le=100, description="Match score")
    reasons: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class TailoredBullet(BaseModel):
    """Tailored bullet with source citations."""

    text: str = Field(description="Tailored bullet text")
    source_ids: list[str] = Field(default_factory=list, description="Source bullet/project ids")


class TailoredResume(BaseModel):
    """Tailored resume with citations."""

    job_id: str = Field(description="Target job identifier")
    bullets: list[TailoredBullet] = Field(default_factory=list)
    summary: str | None = Field(default=None)


class FaithfulnessReport(BaseModel):
    """Faithfulness verification report."""

    overall_score: float = Field(ge=0, le=1, description="Overall faithfulness score")
    supported_bullets: int = Field(description="Number of supported bullets")
    total_bullets: int = Field(description="Total bullets")
    unsupported: list[str] = Field(default_factory=list)


class ApplicationRecord(BaseModel):
    """Application tracker record."""

    id: str = Field(description="Record identifier")
    company: str = Field(description="Company name")
    role: str = Field(description="Role/title")
    url: str | None = Field(default=None)
    match_score: float = Field(ge=0, le=100)
    status: Literal["saved", "applied", "interview", "rejected", "offer", "archived"] = "saved"
    date: datetime = Field(default_factory=datetime.utcnow)
    resume_version: str = Field(description="Resume version identifier")
