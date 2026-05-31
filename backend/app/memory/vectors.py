"""Vector store wrapper — ChromaDB for embedding-based retrieval."""

from __future__ import annotations

from typing import Any

import chromadb
from chromadb.config import Settings

from app.config import CHROMA_PATH


class VectorStore:
    """Lightweight ChromaDB wrapper for similarity search."""

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=Settings(anonymized_telemetry=False),
        )

    def _collection(self, name: str):
        """Get or create a named collection."""
        return self._client.get_or_create_collection(name=name)

    def add(self, collection: str, id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        self._collection(collection).add(
            embeddings=[embedding],
            ids=[id],
            metadatas=[metadata],
        )

    def search(
        self,
        collection: str,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        results = self._collection(collection).query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "score": results["distances"][0][i] if results.get("distances") else None,
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
            })
        return output
