import httpx
from typing import Any

from ..models.schemas import Job


class RemoteOKAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get("https://remoteok.io/api")
                if resp.status_code != 200:
                    return []
                data = resp.json()
                jobs = []
                for item in data[1:50]:  # skip first element (metadata)
                    if not isinstance(item, dict):
                        continue
                    job = Job(
                        id=str(item.get("id", "")),
                        title=item.get("position", "Unknown"),
                        company=item.get("company", "Unknown"),
                        location=item.get("location", "Remote"),
                        description=item.get("description", "")[:500],
                        requirements=[],
                        url=item.get("url", ""),
                        source="remoteok",
                    )
                    jobs.append(job)
                return jobs
        except Exception:
            return []


ADAPTERS = {
    "remoteok": RemoteOKAdapter(),
}
