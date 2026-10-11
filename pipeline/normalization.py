import re

import pandas as pd


def normalize_text(text: str) -> str:
    lines = (line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def normalize_table(table: pd.DataFrame) -> pd.DataFrame:
    normalized = table.dropna(how="all").copy()
    normalized.columns = [str(column).strip() for column in normalized.columns]

    if any(not column for column in normalized.columns):
        raise ValueError("CSV contains an empty column name")
    if len(set(normalized.columns)) != len(normalized.columns):
        raise ValueError("CSV contains duplicate column names")

    return normalized.fillna("")

