from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".csv", ".txt"}


def discover_files(data_dir: Path) -> list[Path]:
    if not data_dir.is_dir():
        raise NotADirectoryError(f"Data directory not found: {data_dir}")

    return sorted(
        path
        for path in data_dir.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


if __name__ == "__main__":
    for file_path in discover_files(Path("data")):
        print(file_path)
