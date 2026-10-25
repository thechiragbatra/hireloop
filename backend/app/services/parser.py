import io
import logging
import uuid
from typing import cast

from docx import Document
from pypdf import PdfReader

from app.core.config import get_llm_client
from app.core.logging import log_safe
from app.llm.client import FakeLLMClient, LLMClient
from app.llm.prompts import PARSE_PROFILE_PROMPT
from app.models.schemas import Profile

logger = logging.getLogger(__name__)


class ResumeParser:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or get_llm_client()

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

    def _empty_profile(self, profile_id: str) -> Profile:
        return Profile(
            id=profile_id,
            skills=[],
            experience=[],
            education=[],
            projects=[],
        )

    async def _parse_structured(self, raw_text: str, profile_id: str) -> Profile:
        if isinstance(self.llm, FakeLLMClient) or not raw_text.strip():
            return self._empty_profile(profile_id)
        try:
            prompt = PARSE_PROFILE_PROMPT.format(raw_text=raw_text[:12000])
            parsed = cast(Profile, await self.llm.complete_structured(Profile, prompt))
            if parsed.id != profile_id:
                parsed.id = profile_id
            return parsed
        except Exception as exc:  # noqa: BLE001
            log_safe(logger, "LLM profile extraction failed", error=str(exc)[:200])
            return self._empty_profile(profile_id)

    async def parse(self, filename: str, content: bytes) -> tuple[Profile, str]:
        ext = filename.lower().split(".")[-1]
        if ext == "pdf":
            raw_text = self.parse_pdf(content)
        elif ext in ("docx", "doc"):
            raw_text = self.parse_docx(content)
        else:
            raise ValueError("Unsupported file type")
        profile_id = str(uuid.uuid4())
        profile = await self._parse_structured(raw_text, profile_id)
        return profile, raw_text
