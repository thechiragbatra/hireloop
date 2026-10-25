
from ..models.schemas import Profile


class ProfileChunker:
    def chunk(self, profile: Profile) -> list[dict]:
        chunks: list[dict] = []
        for exp in profile.experience:
            for bullet in exp.bullets:
                chunks.append({"id": bullet.id, "text": bullet.text, "source": "experience"})
        for proj in profile.projects:
            for bullet in proj.bullets:
                chunks.append({"id": bullet.id, "text": bullet.text, "source": "project"})
        if profile.skills:
            chunks.append({"id": "skills", "text": ", ".join(profile.skills), "source": "skill"})
        return chunks
