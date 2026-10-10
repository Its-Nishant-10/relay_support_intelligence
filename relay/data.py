from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "customer_support_tickets.csv"
SENTIMENT_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "sentiment.csv"


def clean_support_tickets(frame: pd.DataFrame) -> pd.DataFrame:
    """Create intake-time text and retain only supervised learning fields."""
    required = {"subject", "body", "type", "priority", "queue"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Support dataset is missing columns: {sorted(missing)}")
    clean = frame.dropna(subset=["type", "priority", "queue"]).copy()
    for column in required:
        clean[column] = clean[column].fillna("").astype(str).str.strip()
    clean["text"] = (
        (clean["subject"] + " " + clean["body"])
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    clean = clean[clean["text"].str.len() >= 10].drop_duplicates(subset=["text"])
    return clean[
        (
            ["text", "type", "priority", "queue", "language"]
            if "language" in clean
            else ["text", "type", "priority", "queue"]
        )
    ]


def load_public_support_tickets(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw public dataset downloaded by scripts/download_dataset.py."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            "Public dataset not found. Run `python scripts/download_dataset.py` first."
        )
    return pd.read_csv(path)


def load_training_tickets(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    return clean_support_tickets(load_public_support_tickets(path))


def load_sentiment_dataset(path: str | Path = SENTIMENT_DATA_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            "Sentiment dataset not found. Run `python scripts/download_dataset.py` first."
        )
    return pd.read_csv(path).dropna(subset=["text", "label"])
