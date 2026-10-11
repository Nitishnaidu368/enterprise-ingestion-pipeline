from pathlib import Path

from pipeline.embeddings import SentenceTransformerEmbedder
from pipeline.ingestion import ingest_directory
from storage.manifest import Manifest
from storage.vector_store import VectorStore


def main() -> int:
    state_dir = Path(".state")
    embedder = SentenceTransformerEmbedder()
    vector_store = VectorStore(state_dir / "chroma")

    with Manifest(state_dir / "manifest.db") as manifest:
        summary = ingest_directory(Path("data"), manifest, vector_store, embedder)

    print(
        f"Discovered: {summary.discovered} | "
        f"Ingested: {summary.ingested} | "
        f"Skipped: {summary.skipped} | "
        f"Failed: {summary.failed} | "
        f"Chunks: {summary.chunks}"
    )
    for source_path, error in summary.failures.items():
        print(f"FAILED {source_path}: {error}")

    return 1 if summary.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

