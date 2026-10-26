import hashlib
import io
import re
import uuid

from docx import Document
from pypdf import PdfReader

from ..models.schemas import Bullet, Contact, EducationItem, ExperienceItem, Profile, ProjectItem


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

    def _extract_contact(self, text: str) -> Contact:
        email = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        phone = re.findall(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        linkedin = re.findall(r"(https?://(?:www\.)?linkedin\.com/in/[\w\.-]+)", text)
        github = re.findall(r"(https?://(?:www\.)?github\.com/[\w\.-]+)", text)
        website = re.findall(r"(https?://(?!www\.linkedin|www\.github)[\w\.-]+\.[\w\.-]+/[\w\.-/]*)", text)
        return Contact(
            email=email[0] if email else None,
            phone=phone[0] if phone else None,
            linkedin=linkedin[0] if linkedin else None,
            github=github[0] if github else None,
            website=website[0] if website else None,
        )

    def _extract_skills(self, text: str) -> list[str]:
        common = ["python", "javascript", "typescript", "react", "fastapi", "node", "sql", "postgres", "aws", "docker", "git"]
        found = []
        tl = text.lower()
        for s in common:
            if s in tl and s.title() not in found and s.upper() not in found:
                found.append(s.title() if s not in ["sql", "aws"] else s.upper())
        return found

    def parse(self, filename: str, content: bytes) -> tuple[Profile, str]:
        ext = filename.lower().split(".")[-1]
        if ext == "pdf":
            raw_text = self.parse_pdf(content)
        elif ext in ("docx", "doc"):
            raw_text = self.parse_docx(content)
        else:
            raise ValueError("Unsupported file type")
        hashlib.sha256(content).hexdigest()
        contact = self._extract_contact(raw_text)
        skills = self._extract_skills(raw_text)
        profile = Profile(
            id=str(uuid.uuid4()),
            contact=contact,
            skills=skills,
            experience=[
                ExperienceItem(
                    id=str(uuid.uuid4()),
                    company="",
                    title="",
                    bullets=[Bullet(id=str(uuid.uuid4()), text="")],
                )
            ],
            projects=[
                ProjectItem(
                    id=str(uuid.uuid4()),
                    name="",
                    bullets=[Bullet(id=str(uuid.uuid4()), text="")],
                    technologies=[],
                )
            ],
            education=[EducationItem(id=str(uuid.uuid4()), institution="")],
        )
        return profile, raw_text
