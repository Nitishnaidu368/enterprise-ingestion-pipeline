from pathlib import Path

import chromadb

from models.document import Document


class VectorStore:
    def __init__(self, persist_directory: Path, collection_name: str = "enterprise_documents") -> None:
        persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        if len(documents) != len(embeddings):
            raise ValueError("Each document must have one embedding")
        if not documents:
            return

        self.collection.upsert(
            ids=[document.id for document in documents],
            documents=[document.content for document in documents],
            metadatas=[document.metadata for document in documents],
            embeddings=embeddings,
        )

    def count(self) -> int:
        return self.collection.count()

