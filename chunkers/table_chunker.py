from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class TableChunk:
    content: str
    row_start: int
    row_end: int


def chunk_table(table: pd.DataFrame, rows_per_chunk: int = 20) -> list[TableChunk]:
    if rows_per_chunk <= 0:
        raise ValueError("rows_per_chunk must be greater than zero")

    chunks = []
    for start in range(0, len(table), rows_per_chunk):
        rows = table.iloc[start:start + rows_per_chunk]
        chunks.append(TableChunk(
            content=rows.to_csv(index=False).strip(),
            row_start=start + 1,
            row_end=start + len(rows),
        ))

    return chunks


if __name__ == "__main__":
    sample = pd.DataFrame({"id": range(25), "value": range(100, 125)})
    chunks = chunk_table(sample)
    assert [(chunk.row_start, chunk.row_end) for chunk in chunks] == [(1, 20), (21, 25)]
    assert all(chunk.content.startswith("id,value\n") for chunk in chunks)
    print("Table chunking OK")

