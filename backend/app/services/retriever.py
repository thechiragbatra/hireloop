import math
import os
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class HybridRetriever:
    """Keyword/TF-IDF based hybrid retriever (no ML dependencies).

    Kept dependency-free per the Phase-1 ML TODO (torch/sentence-transformers/faiss).
    """

    def __init__(self, index_dir: str = "./data/faiss"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self._docs: list[tuple[str, str]] = []
        self._idf: dict[str, float] = {}
        self._vecs: list[Counter] = []

    def build_index(self, items: list[tuple[str, str]]):
        """items: list of (id, text)."""
        self._docs = list(items)
        self._vecs = []
        df: Counter[str] = Counter()
        for _, text in self._docs:
            tf = Counter(_tokenize(text))
            self._vecs.append(tf)
            for term in tf:
                df[term] += 1
        n = max(len(self._docs), 1)
        self._idf = {term: math.log(n / (1 + cnt)) + 1.0 for term, cnt in df.items()}

    def _tfidf(self, tf: Counter[str]) -> dict[str, float]:
        total = max(sum(tf.values()), 1)
        return {term: (count / total) * self._idf.get(term, 0.0) for term, count in tf.items()}

    def _cosine(self, a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(a.get(t, 0.0) * b.get(t, 0.0) for t in a)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def search_hybrid(self, query: str, top_k: int = 50):
        if not self._docs:
            return []
        q_tf = Counter(_tokenize(query))
        q_vec = self._tfidf(q_tf)
        scores = [
            (doc_id, self._cosine(q_vec, self._tfidf(vec)))
            for (doc_id, _), vec in zip(self._docs, self._vecs)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def rerank(self, query: str, candidates: list[tuple[str, float]]):
        # Simple rerank: boost exact phrase matches
        q_tokens = set(_tokenize(query))
        boosted = []
        for doc_id, score in candidates:
            text = dict(self._docs).get(doc_id, "")
            text_tokens = set(_tokenize(text))
            overlap = len(q_tokens & text_tokens)
            boosted.append((doc_id, score + 0.05 * overlap))
        boosted.sort(key=lambda x: x[1], reverse=True)
        return boosted
