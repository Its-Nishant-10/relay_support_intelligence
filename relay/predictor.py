from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "models"


@dataclass
class Prediction:
    category: str
    priority: str
    queue: str
    sentiment: str
    confidence: float
    confidence_basis: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Predictor:
    """Inference-only service. It never fits or mutates model artifacts."""

    def __init__(self, model_dir: str | Path = MODEL_DIR) -> None:
        self.model_dir = Path(model_dir)
        names = ("category", "priority", "queue", "sentiment")
        missing = [
            name
            for name in names
            if not (self.model_dir / f"{name}_model.joblib").exists()
        ]
        if missing:
            raise FileNotFoundError(
                "Missing trained artifacts: "
                + ", ".join(missing)
                + ". Run `python scripts/download_dataset.py` and `python scripts/train.py`."
            )
        self.models = {
            name: joblib.load(self.model_dir / f"{name}_model.joblib") for name in names
        }

    @staticmethod
    def _predict_with_confidence(model: Any, text: str) -> tuple[str, float]:
        prediction = str(model.predict([text])[0])
        if hasattr(model, "predict_proba"):
            confidence = float(model.predict_proba([text]).max())
        else:
            raise TypeError("Saved model must expose calibrated predict_proba().")
        return prediction, confidence

    def predict_ticket(self, text: str) -> Prediction:
        normalized = " ".join(str(text).split())
        if len(normalized) < 10:
            raise ValueError(
                "Please provide a subject and a more detailed description."
            )
        outputs = {
            name: self._predict_with_confidence(model, normalized)
            for name, model in self.models.items()
        }
        category, category_confidence = outputs["category"]
        priority, priority_confidence = outputs["priority"]
        queue, queue_confidence = outputs["queue"]
        sentiment, sentiment_confidence = outputs["sentiment"]
        return Prediction(
            category=category,
            priority=priority,
            queue=queue,
            sentiment=sentiment,
            confidence=(
                category_confidence
                + priority_confidence
                + queue_confidence
                + sentiment_confidence
            )
            / 4,
            confidence_basis="mean calibrated probability across four models",
        )

    def predict_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        required = {"subject", "description"}
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"CSV must include columns: {', '.join(sorted(required))}")
        result = frame.copy()
        result["text"] = (
            result["subject"].fillna("").astype(str)
            + " "
            + result["description"].fillna("").astype(str)
        ).str.strip()
        predictions = [self.predict_ticket(text).to_dict() for text in result["text"]]
        prediction_frame = pd.DataFrame(predictions)
        return pd.concat([result.drop(columns=["text"]), prediction_frame], axis=1)
