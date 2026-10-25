from typing import List, Dict, Any
import hashlib
from datetime import datetime
from ..models.schemas import JobPosting

class JobSourceAdapter:
    async def fetch(self, filters: Dict[str, Any]) -> List[JobPosting]:
        raise NotImplementedError

class GreenhouseAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[JobPosting]:
        # Placeholder - no real scraping, structure only
        return []

class LeverAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[JobPosting]:
        return []

class AshbyAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[JobPosting]:
        return []

class AdzunaAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[JobPosting]:
        return []

class RemoteOKAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[JobPosting]:
        return []

class CustomCareerPageAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[JobPosting]:
        return []

ADAPTERS = {
    "greenhouse": GreenhouseAdapter(),
    "lever": LeverAdapter(),
    "ashby": AshbyAdapter(),
    "adzuna": AdzunaAdapter(),
    "remoteok": RemoteOKAdapter(),
    "custom": CustomCareerPageAdapter(),
}

def job_hash(j: Dict[str, Any]) -> str:
    key = f"{j.get('source_url','')}|{j.get('title','')}|{j.get('company','')}"
    return hashlib.sha256(key.encode()).hexdigest()
