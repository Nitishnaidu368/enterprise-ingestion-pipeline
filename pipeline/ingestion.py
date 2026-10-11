from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from chunkers.table_chunker import chunk_table
from chunkers.text_chunker import chunk_text
from models.document import Document
from parsers.pdf_parser import parse_pdf
from parsers.table_parser import parse_csv
from parsers.text_parser import parse_text
from pipeline.discovery import discover_files
from pipeline.metadata import build_document
from pipeline.normalization import normalize_table, normalize_text
from pipeline.router import detect_file_type
from storage.manifest import Manifest


class Embedder(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...


class DocumentStore(Protocol):
    def upsert(self, documents: list[Document], embeddings: list[list[float]]) -> None: ...


@dataclass(slots=True)
class IngestionSummary:
    discovered: int = 0
    ingested: int = 0
    skipped: int = 0
    failed: int = 0
    chunks: int = 0
    failures: dict[str, str] = field(default_factory=dict)


def prepare_documents(file_path: Path, data_dir: Path) -> list[Document]:
    file_type = detect_file_type(file_path)
    source_path = file_path.resolve().relative_to(data_dir.resolve()).as_posix()
    documents: list[Document] = []

    if file_type == "txt":
        text = normalize_text(parse_text(file_path))
        for chunk_index, content in enumerate(chunk_text(text)):
            documents.append(build_document(content, source_path, file_type, chunk_index))

    elif file_type == "pdf":
        chunk_index = 0
        for page_number, page in enumerate(parse_pdf(file_path), start=1):
            for content in chunk_text(normalize_text(page)):
                documents.append(build_document(
                    content,
                    source_path,
                    file_type,
                    chunk_index,
                    page_number=page_number,
                ))
                chunk_index += 1

    elif file_type == "csv":
        table = normalize_table(parse_csv(file_path))
        for chunk_index, table_chunk in enumerate(chunk_table(table)):
            documents.append(build_document(
                table_chunk.content,
                source_path,
                file_type,
                chunk_index,
                row_start=table_chunk.row_start,
                row_end=table_chunk.row_end,
            ))

    if not documents:
        raise ValueError(f"No extractable content found: {file_path}")

    return documents


def ingest_directory(
    data_dir: Path,
    manifest: Manifest,
    vector_store: DocumentStore,
    embedder: Embedder,
) -> IngestionSummary:
    files = discover_files(data_dir)
    summary = IngestionSummary(discovered=len(files))

    for file_path in files:
        manifest_path = str(file_path.resolve())
        file_type = detect_file_type(file_path)

        # ponytail: completed paths are skipped in the MVP; add checksums and
        # stale-chunk deletion before supporting changed files.
        if manifest.is_completed(manifest_path):
            summary.skipped += 1
            continue

        manifest.mark_started(manifest_path, file_type)
        try:
            documents = prepare_documents(file_path, data_dir)
            embeddings = embedder.embed_documents([document.content for document in documents])
            vector_store.upsert(documents, embeddings)
            manifest.mark_completed(manifest_path, len(documents))
            summary.ingested += 1
            summary.chunks += len(documents)
        except Exception as error:
            message = str(error) or type(error).__name__
            manifest.mark_failed(manifest_path, file_type, message)
            summary.failed += 1
            summary.failures[file_path.as_posix()] = message

    return summary

