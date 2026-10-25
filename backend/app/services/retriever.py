from typing import List, Tuple
import os

# Minimal retriever scaffold (will be extended)
class HybridRetriever:
    def __init__(self, index_dir: str = "./data/faiss"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)

    def build_index(self, items: List[Tuple[str, str]]):
        # items: (id, text)
        pass

    def search_hybrid(self, query: str, top_k: int = 50):
        return []

    def rerank(self, query: str, candidates: List[Tuple[str, float]]):
        return candidates
