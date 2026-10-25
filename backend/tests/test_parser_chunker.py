from app.services.parser import ResumeParser
from app.services.chunker import ProfileChunker
from app.models.schemas import ResumeProfile

def test_parser_docx_placeholder():
    p = ResumeParser()
    # Just test class exists
    assert hasattr(p, 'parse')

def test_chunker_empty():
    c = ProfileChunker()
    prof = ResumeProfile(profile_id='x')
    chunks = c.chunk(prof)
    assert isinstance(chunks, list)
