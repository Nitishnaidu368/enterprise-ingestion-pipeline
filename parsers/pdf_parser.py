from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


def parse_pdf(file_path: Path) -> list[str]:
    if not file_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        if reader.is_encrypted:
            raise ValueError(f"Encrypted PDFs are not supported: {file_path}")

        # ponytail: pypdf extracts embedded text only; add OCR when scanned
        # documents enter the pipeline.
        return [page.extract_text() or "" for page in reader.pages]
    except PdfReadError as error:
        raise ValueError(f"Could not read PDF: {file_path}") from error


if __name__ == "__main__":
    sample = Path("data/pdf/refund_policy.pdf")
    pages = parse_pdf(sample)
    assert pages and "Enterprise Refund Policy" in pages[0]
    print(f"Parsed {len(pages)} page(s) from {sample}")
