from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_POLICY_PATH = PROJECT_ROOT / "config" / "business_rules.json"


@dataclass
class PolicyDecision:
    priority: str
    queue: str
    human_review: bool
    applied_rules: list[str]
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_policy(path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def save_policy(policy: dict[str, Any], path: str | Path = DEFAULT_POLICY_PATH) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(policy, handle, indent=2)


def apply_policy(text: str, prediction: Any, policy: dict[str, Any]) -> PolicyDecision:
    priority = prediction.priority
    queue = prediction.queue
    applied: list[str] = []
    normalized = text.lower()
    for rule in policy.get("keyword_priority_overrides", []):
        if not rule.get("enabled", True):
            continue
        if any(keyword.lower() in normalized for keyword in rule.get("keywords", [])):
            priority = rule["priority"]
            applied.append(rule["description"])
    for rule in policy.get("category_priority_overrides", []):
        if not rule.get("enabled", True):
            continue
        if prediction.category.lower() == rule["category"].lower():
            priority = rule["priority"]
            applied.append(rule["description"])
    for rule in policy.get("queue_overrides", []):
        if not rule.get("enabled", True):
            continue
        if prediction.category.lower() == rule["category"].lower():
            queue = rule["queue"]
            applied.append(rule["description"])
    human_review = prediction.confidence < float(
        policy.get("confidence_threshold", 0.50)
    )
    if human_review:
        applied.append(
            f"Confidence below {float(policy.get('confidence_threshold', 0.50)):.0%}"
        )
    for rule in policy.get("keyword_review_overrides", []):
        if not rule.get("enabled", True):
            continue
        if any(keyword.lower() in normalized for keyword in rule.get("keywords", [])):
            human_review = True
            applied.append(rule["description"])
    for category in policy.get("mandatory_review_categories", []):
        if prediction.category.lower() == category.lower():
            human_review = True
            applied.append(f"Mandatory review for {category} tickets")
    explanation = "ML prediction accepted as-is."
    if applied:
        explanation = "Applied: " + "; ".join(applied)
    return PolicyDecision(priority, queue, human_review, applied, explanation)
