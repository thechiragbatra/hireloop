from typing import Any

from ..models.schemas import Job


class JobSourceAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        raise NotImplementedError


class GreenhouseAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        return []


class LeverAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        return []


class AshbyAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        return []


class AdzunaAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        return []


class RemoteOKAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        return []


class CustomCareerPageAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        return []


ADAPTERS = {
    "greenhouse": GreenhouseAdapter(),
    "lever": LeverAdapter(),
    "ashby": AshbyAdapter(),
    "adzuna": AdzunaAdapter(),
    "remoteok": RemoteOKAdapter(),
    "custom": CustomCareerPageAdapter(),
}
