from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from relay.policy import apply_policy
from relay.predictor import Predictor


def make_model(path: Path, labels: list[str]) -> None:
    model = Pipeline(
        [("tfidf", TfidfVectorizer()), ("classifier", LogisticRegression(max_iter=300))]
    )
    model.fit(
        [
            "billing payment refund",
            "technical crash outage",
            "account login password",
            "product feature question",
        ],
        labels,
    )
    joblib.dump(model, path)


def test_predictor_loads_saved_models_and_predicts_new_text(tmp_path: Path) -> None:
    for name, labels in {
        "category": ["billing", "technical", "account", "product"],
        "priority": ["high", "high", "medium", "low"],
        "queue": ["billing", "technical", "account", "product"],
        "sentiment": ["negative", "negative", "negative", "positive"],
    }.items():
        make_model(tmp_path / f"{name}_model.joblib", labels)
    predictor = Predictor(tmp_path)
    result = predictor.predict_ticket("Please refund this payment")
    assert result.category in {"billing", "technical", "account", "product"}
    assert 0 <= result.confidence <= 1


def test_policy_changes_final_decision_without_changing_prediction() -> None:
    prediction = type(
        "Prediction",
        (),
        {
            "category": "billing",
            "priority": "low",
            "queue": "general",
            "confidence": 0.95,
        },
    )()
    policy = {
        "confidence_threshold": 0.8,
        "keyword_priority_overrides": [
            {
                "keywords": ["refund"],
                "priority": "high",
                "description": "Refunds are high priority",
            }
        ],
        "mandatory_review_categories": [],
        "queue_overrides": [
            {
                "category": "billing",
                "queue": "Billing & Payments",
                "description": "Billing queue",
            }
        ],
    }
    decision = apply_policy("refund requested", prediction, policy)
    assert prediction.priority == "low"
    assert decision.priority == "high"
    assert decision.queue == "Billing & Payments"
    assert decision.human_review is False


def test_policy_requires_review_for_security_keywords() -> None:
    prediction = type(
        "Prediction",
        (),
        {
            "category": "Incident",
            "priority": "high",
            "queue": "IT Support",
            "confidence": 0.95,
        },
    )()
    decision = apply_policy(
        "Unauthorized account takeover",
        prediction,
        {
            "confidence_threshold": 0.5,
            "keyword_review_overrides": [
                {
                    "keywords": ["unauthorized", "account takeover"],
                    "description": "Security review",
                }
            ],
        },
    )
    assert decision.human_review is True
    assert decision.applied_rules == ["Security review"]


def test_disabled_policy_rule_does_not_change_decision() -> None:
    prediction = type(
        "Prediction",
        (),
        {
            "category": "billing",
            "priority": "low",
            "queue": "General Support",
            "confidence": 0.95,
        },
    )()
    decision = apply_policy(
        "refund requested",
        prediction,
        {
            "confidence_threshold": 0.5,
            "keyword_priority_overrides": [
                {
                    "keywords": ["refund"],
                    "priority": "high",
                    "description": "Disabled refund rule",
                    "enabled": False,
                }
            ],
        },
    )
    assert decision.priority == "low"
    assert decision.applied_rules == []


def test_batch_input_validation(tmp_path: Path) -> None:
    for name, labels in {
        "category": ["billing", "technical", "account", "product"],
        "priority": ["high", "high", "medium", "low"],
        "queue": ["billing", "technical", "account", "product"],
        "sentiment": ["negative", "negative", "negative", "positive"],
    }.items():
        make_model(tmp_path / f"{name}_model.joblib", labels)
    with __import__("pytest").raises(ValueError, match="subject"):
        Predictor(tmp_path).predict_frame(pd.DataFrame({"body": ["hello"]}))
