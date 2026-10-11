# Enterprise Multimodal Data Ingestion Pipeline

A learning-focused RAG ingestion MVP for PDF, CSV, and TXT files.

## Pipeline

```text
Discovery -> Type Detection -> Parsing -> Normalization -> Chunking
          -> Metadata -> Embeddings -> ChromaDB
                              |
                              +-> SQLite ingestion manifest
```

PDF and TXT content use 800-character chunks with 100-character overlap. CSV files use 20-row chunks and repeat the column headers in every chunk.

## Setup

Python 3.12 is recommended.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Place source documents under `data/pdf`, `data/tables`, or `data/text`, then run:

```bash
python main.py
```

The first run downloads the `all-MiniLM-L6-v2` sentence-transformer model. Runtime data is stored under `.state/`. A second run skips paths already marked complete in the SQLite manifest.

Run the offline test suite with:

```bash
python -m unittest discover -s tests -v
```

## MVP limits

- File types are detected by extension.
- PDFs must contain embedded text; scanned documents need OCR.
- TXT and CSV inputs must be UTF-8; CSV files must be comma-delimited with headers.
- The manifest tracks completed paths, not content checksums. Clear `.state/` to re-ingest changed files.
- Excel, images, document versioning, stale-chunk deletion, ACL metadata, retries, parallelism, and production metrics are deferred.
