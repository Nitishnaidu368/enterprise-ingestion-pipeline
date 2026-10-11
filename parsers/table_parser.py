from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def parse_csv(file_path: Path) -> pd.DataFrame:
    if not file_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    # ponytail: the MVP expects UTF-8, comma-delimited files with headers;
    # add schema, encoding, and delimiter detection for broader sources.
    try:
        return pd.read_csv(file_path, encoding="utf-8")
    except (EmptyDataError, ParserError, UnicodeDecodeError) as error:
        raise ValueError(f"Could not read CSV: {file_path}") from error


if __name__ == "__main__":
    sample = Path("data/tables/payments.csv")
    table = parse_csv(sample)
    assert list(table.columns) == [
        "payment_id",
        "customer_id",
        "amount",
        "currency",
        "status",
        "reason_code",
    ]
    assert len(table) == 6
    print(f"Parsed {len(table)} rows and {len(table.columns)} columns from {sample}")
