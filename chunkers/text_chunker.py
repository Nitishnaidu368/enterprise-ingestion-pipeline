def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size")
    if not text:
        return []

    chunks = []
    start = 0

    # ponytail: fixed character windows are the MVP ceiling; replace this with
    # structural or token-aware splitting when retrieval quality requires it.
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap

    return chunks


if __name__ == "__main__":
    assert chunk_text("abcdefghij", chunk_size=6, overlap=2) == ["abcdef", "efghij"]
    print("Text chunking OK")

