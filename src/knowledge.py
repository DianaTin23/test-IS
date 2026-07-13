from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .crawler import Document

INDEX_PATH = Path("data/index.json")


@dataclass
class Hit:
    document: Document
    score: float


def save_documents(documents: list[Document], path: Path = INDEX_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = {f"{doc.source_id}:{doc.content_hash}": doc.to_dict() for doc in documents}
    path.write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2), encoding="utf-8")


def load_documents(path: Path = INDEX_PATH) -> list[Document]:
    if not path.exists():
        return []
    return [Document(**item) for item in json.loads(path.read_text(encoding="utf-8"))]


def search(question: str, documents: list[Document], limit: int = 4) -> list[Hit]:
    if not question.strip() or not documents:
        return []
    texts = [doc.text for doc in documents]
    matrix = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=20_000).fit_transform(
        texts + [question]
    )
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    indices = scores.argsort()[::-1][:limit]
    return [Hit(documents[index], float(scores[index])) for index in indices if scores[index] > 0]

