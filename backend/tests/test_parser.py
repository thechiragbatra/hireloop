import io

import anyio
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
    profile, raw_text = anyio.run(parser.parse, "resume.docx", content)
    assert profile.id
    assert profile.skills == []
    assert raw_text == "Hello World"


def test_parse_pdf_round_trip():
    parser = ResumeParser()
    content = _make_pdf()
    profile, raw_text = anyio.run(parser.parse, "resume.pdf", content)
    assert profile.id
    assert isinstance(raw_text, str)


def test_parse_unsupported_type_raises():
    parser = ResumeParser()
    try:
        anyio.run(parser.parse, "resume.txt", b"hello")
    except ValueError:
        return
    raise AssertionError("Expected ValueError for unsupported file type")
