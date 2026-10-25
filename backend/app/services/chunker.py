from typing import List
import uuid
from ..models.schemas import ResumeProfile, ProfileChunk

class ProfileChunker:
    def chunk(self, profile: ResumeProfile) -> List[ProfileChunk]:
        chunks: List[ProfileChunk] = []
        # Chunk summary
        if profile.summary:
            chunks.append(ProfileChunk(
                chunk_id=str(uuid.uuid4()),
                source_type="summary",
                source_ref="summary",
                text=profile.summary
            ))
        # Chunk experience bullets
        for ei, exp in enumerate(profile.experience):
            for bi, bullet in enumerate(exp.bullets):
                chunks.append(ProfileChunk(
                    chunk_id=str(uuid.uuid4()),
                    source_type="experience",
                    source_ref=f"exp[{ei}].bullets[{bi}]",
                    text=bullet
                ))
        # Chunk projects
        for pi, proj in enumerate(profile.projects):
            for bi, bullet in enumerate(proj.bullets):
                chunks.append(ProfileChunk(
                    chunk_id=str(uuid.uuid4()),
                    source_type="project",
                    source_ref=f"proj[{pi}].bullets[{bi}]",
                    text=bullet
                ))
        # Chunk skills
        if profile.skills.technical or profile.skills.tools:
            skills_text = ", ".join(profile.skills.technical + profile.skills.tools)
            chunks.append(ProfileChunk(
                chunk_id=str(uuid.uuid4()),
                source_type="skill",
                source_ref="skills.technical+tools",
                text=skills_text
            ))
        return chunks
