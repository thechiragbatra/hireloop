from app.services.retriever import HybridRetriever


def test_retriever_build_and_search():
    retriever = HybridRetriever()
    items = [
        ("d1", "Python FastAPI backend engineer"),
        ("d2", "React frontend developer TypeScript"),
        ("d3", "Python data science machine learning"),
    ]
    retriever.build_index(items)
    results = retriever.search_hybrid("Python backend", top_k=2)
    assert len(results) == 2
    assert results[0][0] == "d1"
    assert results[0][1] > 0


def test_retriever_empty():
    retriever = HybridRetriever()
    assert retriever.search_hybrid("anything") == []


def test_retriever_rerank():
    retriever = HybridRetriever()
    items = [("d1", "Python FastAPI backend"), ("d2", "Java spring backend")]
    retriever.build_index(items)
    candidates = [("d2", 0.1), ("d1", 0.2)]
    reranked = retriever.rerank("Python", candidates)
    assert reranked[0][0] == "d1"
