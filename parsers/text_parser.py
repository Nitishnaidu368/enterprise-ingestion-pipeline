from pathlib import Path


def parse_text(file_path: Path) -> str:
    if not file_path.is_file():
        raise FileNotFoundError(f"Text file not found: {file_path}")

    # ponytail: UTF-8 covers the MVP; add encoding detection when real sources
    # include legacy encodings.
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"Text file is not valid UTF-8: {file_path}") from error


if __name__ == "__main__":
    sample = Path("data/text/refund_policy.txt")
    text = parse_text(sample)
    assert "Enterprise Refund Policy" in text
    print(f"Parsed {len(text)} characters from {sample}")
