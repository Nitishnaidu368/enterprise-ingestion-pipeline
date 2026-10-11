import tempfile
import unittest
from pathlib import Path

import pandas as pd

from chunkers.table_chunker import chunk_table
from chunkers.text_chunker import chunk_text
from pipeline.ingestion import ingest_directory
from storage.manifest import Manifest
from storage.vector_store import VectorStore


class FakeEmbedder:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text)), 1.0, 0.0] for text in texts]


class PipelineTests(unittest.TestCase):
    def test_text_chunk_overlap(self) -> None:
        self.assertEqual(
            chunk_text("abcdefghij", chunk_size=6, overlap=2),
            ["abcdef", "efghij"],
        )

    def test_table_chunks_repeat_headers(self) -> None:
        chunks = chunk_table(pd.DataFrame({"id": range(25), "value": range(25)}))
        self.assertEqual([(chunk.row_start, chunk.row_end) for chunk in chunks], [(1, 20), (21, 25)])
        self.assertTrue(all(chunk.content.startswith("id,value\n") for chunk in chunks))

    def test_ingestion_and_manifest_skip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dir = root / "data"
            (data_dir / "text").mkdir(parents=True)
            (data_dir / "tables").mkdir()
            (data_dir / "text" / "note.txt").write_text("A short policy document.", encoding="utf-8")
            (data_dir / "tables" / "items.csv").write_text("id,name\n1,Alpha\n2,Beta\n", encoding="utf-8")

            vector_store = VectorStore(root / "chroma", "test_documents")
            with Manifest(root / "manifest.db") as manifest:
                first = ingest_directory(data_dir, manifest, vector_store, FakeEmbedder())
                second = ingest_directory(data_dir, manifest, vector_store, FakeEmbedder())

            self.assertEqual((first.discovered, first.ingested, first.failed, first.chunks), (2, 2, 0, 2))
            self.assertEqual((second.discovered, second.skipped), (2, 2))
            self.assertEqual(vector_store.count(), 2)


if __name__ == "__main__":
    unittest.main()

