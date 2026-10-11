from pathlib import Path

from pipeline.discovery import SUPPORTED_EXTENSIONS


def detect_file_type(file_path: Path) -> str:
    extension = file_path.suffix.lower()

    # ponytail: extensions are enough for trusted MVP files; inspect MIME types
    # and file signatures when ingestion accepts untrusted uploads.
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension or '<none>'}")

    return extension.removeprefix(".")


if __name__ == "__main__":
    assert detect_file_type(Path("example.PDF")) == "pdf"
    assert detect_file_type(Path("example.csv")) == "csv"
    assert detect_file_type(Path("example.txt")) == "txt"
    print("File type detection OK")
