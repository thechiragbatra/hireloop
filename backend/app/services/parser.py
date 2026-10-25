from typing import Tuple
from pypdf import PdfReader
from docx import Document
import io
import hashlib

from ..models.schemas import ResumeProfile, ContactInfo, ExperienceItem, EducationItem, ProjectItem, SkillSet

class ResumeParser:
    def parse_pdf(self, content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        text = []
        for page in reader.pages:
            try:
                text.append(page.extract_text() or "")
            except Exception:
                pass
        return "\n".join(text)

    def parse_docx(self, content: bytes) -> str:
        doc = Document(io.BytesIO(content))
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text)

    def parse(self, filename: str, content: bytes) -> Tuple[ResumeProfile, str]:
        ext = filename.lower().split(".")[-1]
        if ext == "pdf":
            raw_text = self.parse_pdf(content)
        elif ext in ("docx", "doc"):
            raw_text = self.parse_docx(content)
        else:
            raise ValueError("Unsupported file type")
        raw_hash = hashlib.sha256(content).hexdigest()
        # Minimal structured extraction placeholder (to be enhanced)
        profile = ResumeProfile(
            profile_id="",
            contact=ContactInfo(),
            summary=None,
            experience=[],
            education=[],
            projects=[],
            skills=SkillSet(),
            raw_hash=raw_hash,
            chunks=[]
        )
        return profile, raw_text
