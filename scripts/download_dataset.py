from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from datasets import load_dataset

ROOT = Path(__file__).parent.parent
RAW = ROOT / "data" / "raw"
SUPPORT_DATASET = "Prady06/customer-support-tickets"
SENTIMENT_DATASET = "SetFit/sst2"


def print_profile(name: str, frame: pd.DataFrame) -> None:
    print(f"\n{name}: {len(frame):,} rows")
    print("Columns:", ", ".join(frame.columns))
    print("Missing values:")
    print(frame.isna().sum().to_string())
    for column in ("type", "priority", "queue", "language", "label"):
        if column in frame:
            print(f"{column} distribution:")
            print(frame[column].value_counts(dropna=False).head(20).to_string())


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    print(f"Downloading public dataset: {SUPPORT_DATASET}")
    support = load_dataset(SUPPORT_DATASET, split="train").to_pandas()
    support.to_csv(RAW / "customer_support_tickets.csv", index=False)
    print_profile("Customer support tickets", support)

    print(f"\nDownloading public sentiment dataset: {SENTIMENT_DATASET}")
    sentiment = load_dataset(SENTIMENT_DATASET, split="train").to_pandas()
    sentiment["label"] = (
        sentiment["label"]
        .map({0: "negative", 1: "positive"})
        .fillna(sentiment["label"].astype(str))
    )
    sentiment[["text", "label"]].to_csv(RAW / "sentiment.csv", index=False)
    print_profile("Sentiment training data", sentiment[["text", "label"]])

    metadata = {
        "support_dataset": SUPPORT_DATASET,
        "support_dataset_description": "Public synthetic IT ticket dataset described by its Hugging Face dataset card.",
        "sentiment_dataset": SENTIMENT_DATASET,
        "downloaded_support_rows": len(support),
        "downloaded_sentiment_rows": len(sentiment),
    }
    (RAW / "dataset_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print("\nSaved raw data under data/raw/")


if __name__ == "__main__":
    main()
