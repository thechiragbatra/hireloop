import io

import pytest
from docx import Document
from pypdf import PdfWriter

from app.services.parser import ResumeParser


def _make_docx(text: str) -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _make_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_parse_docx_returns_profile_and_text():
    parser = ResumeParser()
    content = _make_docx("Hello World")
    profile, raw_text = parser.parse("resume.docx", content)
    assert profile.id
    assert profile.skills == []
    assert raw_text == "Hello World"


def test_parse_blank_pdf_requires_readable_text():
    parser = ResumeParser()
    content = _make_pdf()
    with pytest.raises(ValueError, match="No readable text"):
        parser.parse("resume.pdf", content)


def test_parse_unsupported_type_raises():
    parser = ResumeParser()
    with pytest.raises(ValueError, match="Unsupported file type"):
        parser.parse("resume.txt", b"hello")
