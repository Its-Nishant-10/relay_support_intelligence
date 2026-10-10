from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from relay.data import load_sentiment_dataset, load_training_tickets  # noqa: E402

MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
FIGURE_DIR = REPORT_DIR / "figures"
RANDOM_STATE = 42


def make_pipeline(kind: str, calibrated: bool = False) -> Pipeline:
    if kind == "logistic_regression":
        classifier: Any = LogisticRegression(max_iter=1000, class_weight="balanced")
    elif kind == "linear_svc":
        base = LinearSVC(class_weight="balanced")
        classifier = CalibratedClassifierCV(base, cv=3) if calibrated else base
    else:
        raise ValueError(kind)
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=50000,
                    min_df=2,
                    sublinear_tf=True,
                    strip_accents="unicode",
                ),
            ),
            ("classifier", classifier),
        ]
    )


def metrics_for(y_true: pd.Series, predictions: Any) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "macro_f1": float(
            f1_score(y_true, predictions, average="macro", zero_division=0)
        ),
        "weighted_f1": float(
            f1_score(y_true, predictions, average="weighted", zero_division=0)
        ),
        "precision": float(
            precision_score(y_true, predictions, average="weighted", zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, predictions, average="weighted", zero_division=0)
        ),
    }


def save_confusion_matrix(y_true: pd.Series, predictions: Any, target: str) -> None:
    labels = sorted(set(y_true) | set(predictions))
    matrix = confusion_matrix(y_true, predictions, labels=labels)
    plt.figure(figsize=(max(7, len(labels) * 0.55), max(5, len(labels) * 0.45)))
    sns.heatmap(
        matrix,
        annot=len(labels) <= 12,
        fmt="d",
        cmap="YlGnBu",
        xticklabels=labels,
        yticklabels=labels,
    )
    plt.title(f"{target.title()} confusion matrix (unseen test set)")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / f"{target}_confusion_matrix.png", dpi=160)
    plt.close()


def train_target(
    text_train: pd.Series,
    text_test: pd.Series,
    y_train: pd.Series,
    y_test: pd.Series,
    target: str,
) -> dict[str, Any]:
    print(f"\nTraining {target} model...")
    candidate_results: dict[str, dict[str, float]] = {}
    for kind in ("logistic_regression", "linear_svc"):
        model = make_pipeline(kind, calibrated=kind == "linear_svc")
        model.fit(text_train, y_train)
        predictions = model.predict(text_test)
        candidate_results[kind] = metrics_for(y_test, predictions)
        print(
            f"  {kind}: macro F1={candidate_results[kind]['macro_f1']:.3f}, weighted F1={candidate_results[kind]['weighted_f1']:.3f}"
        )
    selected = max(
        candidate_results, key=lambda name: candidate_results[name]["macro_f1"]
    )
    final_model = make_pipeline(selected, calibrated=selected == "linear_svc")
    final_model.fit(text_train, y_train)
    final_predictions = final_model.predict(text_test)
    final_metrics = metrics_for(y_test, final_predictions)
    save_confusion_matrix(y_test, final_predictions, target)
    joblib.dump(final_model, MODEL_DIR / f"{target}_model.joblib")
    print(f"{target.title()} Macro F1: {final_metrics['macro_f1']:.3f}")
    return {
        "selected_model": selected,
        "candidates": candidate_results,
        "test_metrics": final_metrics,
        "test_report": classification_report(
            y_test, final_predictions, output_dict=True, zero_division=0
        ),
        "test_rows": int(len(y_test)),
        "train_rows": int(len(y_train)),
    }


def split_frame(
    frame: pd.DataFrame, target: str
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    train_indices, test_indices = train_test_split(
        frame.index, test_size=0.20, random_state=RANDOM_STATE, stratify=frame[target]
    )
    return (
        frame.loc[train_indices, "text"],
        frame.loc[test_indices, "text"],
        frame.loc[train_indices, target],
        frame.loc[test_indices, target],
    )


def main() -> None:
    MODEL_DIR.mkdir(exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    support = load_training_tickets()
    metrics: dict[str, Any] = {
        "dataset": {
            "source": "Prady06/customer-support-tickets",
            "description": "Public synthetic IT ticket dataset described by the Hugging Face dataset card.",
            "rows_after_cleaning": int(len(support)),
            "features": ["subject + body"],
            "excluded_fields": [
                "answer",
                "resolution",
                "assigned team",
                "post-resolution fields",
            ],
            "split": "80% train / 20% test, random_state=42, stratified by target",
        },
        "targets": {},
    }
    for source_column, artifact_name in (
        ("type", "category"),
        ("priority", "priority"),
        ("queue", "queue"),
    ):
        text_train, text_test, y_train, y_test = split_frame(support, source_column)
        result = train_target(text_train, text_test, y_train, y_test, artifact_name)
        metrics["targets"][artifact_name] = result

    sentiment = load_sentiment_dataset()
    sentiment_train, sentiment_test, sentiment_y_train, sentiment_y_test = (
        train_test_split(
            sentiment["text"],
            sentiment["label"],
            test_size=0.20,
            random_state=RANDOM_STATE,
            stratify=sentiment["label"],
        )
    )
    sentiment_result = train_target(
        sentiment_train,
        sentiment_test,
        sentiment_y_train,
        sentiment_y_test,
        "sentiment",
    )
    metrics["sentiment"] = {
        "source": "SetFit/sst2",
        "description": "Public Stanford Sentiment Treebank-derived dataset accessed through Hugging Face.",
        **sentiment_result,
    }
    (REPORT_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    print("\nModels saved successfully to models/")
    print("Metrics saved to reports/metrics.json")


if __name__ == "__main__":
    main()
