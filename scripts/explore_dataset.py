from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from relay.data import load_public_support_tickets  # noqa: E402


def main() -> None:
    frame = load_public_support_tickets()
    figures = ROOT / "reports" / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    frame["text_length"] = (
        frame["subject"].fillna("").astype(str)
        + " "
        + frame["body"].fillna("").astype(str)
    ).str.len()
    print(f"Tickets: {len(frame):,}")
    print("Missing values:\n", frame.isna().sum().to_string())
    print(
        "Duplicate subject/body pairs:",
        frame.duplicated(subset=["subject", "body"]).sum(),
    )
    for column in ("type", "priority", "queue", "language"):
        print(
            f"\n{column} distribution:\n{frame[column].value_counts(dropna=False).to_string()}"
        )
    print("\nText length summary:\n", frame["text_length"].describe().to_string())
    sns.set_theme(style="whitegrid")
    for column in ("type", "priority", "language"):
        plt.figure(figsize=(10, 5))
        frame[column].value_counts().head(20).plot(kind="bar", color="#7ea63c")
        plt.title(f"Ticket distribution by {column}")
        plt.ylabel("Tickets")
        plt.tight_layout()
        plt.savefig(figures / f"distribution_{column}.png", dpi=160)
        plt.close()
    plt.figure(figsize=(10, 5))
    sns.histplot(frame["text_length"], bins=40, color="#275d55")
    plt.title("Ticket intake text length distribution")
    plt.xlabel("Characters in subject + body")
    plt.tight_layout()
    plt.savefig(figures / "text_length_distribution.png", dpi=160)
    plt.close()
    print(f"Figures saved to {figures}")


if __name__ == "__main__":
    main()
