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
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search the collection by embedding vector similarity.

        Args:
            collection: Name of the ChromaDB collection.
            query_embedding: The embedding vector to search with.
            top_k: Maximum number of results to return.
            where: Optional metadata filter dict (e.g. ``{"protagonist": "Caelan"}``).

        Returns:
            List of ``{id, score (distance), metadata}`` dicts sorted by
            increasing distance (most similar first).
        """
        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        if where:
            kwargs["where"] = where

        results = self._collection(collection).query(**kwargs)
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "score": results["distances"][0][i] if results.get("distances") else None,
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
            })
        return output
