from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from models.document import Document, MetadataValue


def build_document(
    content: str,
    source_path: str,
    file_type: str,
    chunk_index: int,
    *,
    page_number: int | None = None,
    row_start: int | None = None,
    row_end: int | None = None,
) -> Document:
    metadata: dict[str, MetadataValue] = {
        "source_path": source_path,
        "file_name": Path(source_path).name,
        "file_type": file_type,
        "chunk_index": chunk_index,
    }

    if page_number is not None:
        metadata["page_number"] = page_number
    if row_start is not None:
        metadata["row_start"] = row_start
    if row_end is not None:
        metadata["row_end"] = row_end

    location = f"{page_number or ''}:{row_start or ''}:{row_end or ''}:{chunk_index}"
    document_id = str(uuid5(NAMESPACE_URL, f"{source_path}:{location}"))
    return Document(id=document_id, content=content, metadata=metadata)

