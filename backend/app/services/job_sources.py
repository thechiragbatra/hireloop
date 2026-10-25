from typing import Any, Dict, List

from ..models.schemas import Job


class JobSourceAdapter:
    async def fetch(self, filters: Dict[str, Any]) -> List[Job]:
        raise NotImplementedError


class GreenhouseAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[Job]:
        return []


class LeverAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[Job]:
        return []


class AshbyAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[Job]:
        return []


class AdzunaAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[Job]:
        return []


class RemoteOKAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[Job]:
        return []


class CustomCareerPageAdapter(JobSourceAdapter):
    async def fetch(self, filters: Dict[str, Any]) -> List[Job]:
        return []


ADAPTERS = {
    "greenhouse": GreenhouseAdapter(),
    "lever": LeverAdapter(),
    "ashby": AshbyAdapter(),
    "adzuna": AdzunaAdapter(),
    "remoteok": RemoteOKAdapter(),
    "custom": CustomCareerPageAdapter(),
}
