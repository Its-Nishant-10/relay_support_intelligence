from __future__ import annotations

from datetime import datetime
from typing import Any
import streamlit as st


def brand() -> None:
    st.markdown(
        '<div><span class="relay-mark">R</span><span class="brand-name">Relay</span><div class="brand-subtitle">Support Intelligence</div></div>',
        unsafe_allow_html=True,
    )


def page_header(
    title: str, subtitle: str, eyebrow: str = "Support Intelligence"
) -> None:
    st.markdown(
        f'<div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p class="page-subtitle">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def section_header(title: str, note: str | None = None) -> None:
    st.subheader(title)
    if note:
        st.caption(note)


def badge(label: str, tone: str = "neutral") -> str:
    return f'<span class="status-badge badge-{tone}">{label}</span>'


def confidence_bar(value: float, threshold: float = 0.5) -> None:
    percent = max(0, min(100, value * 100))
    warning = " warning" if value < threshold else ""
    st.markdown(
        f'<div class="confidence-value">{percent:.0f}%</div><div class="confidence-bar"><div class="confidence-fill{warning}" style="width:{percent:.1f}%"></div></div><div class="metric-context">Model confidence</div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, context: str, tone: str = "") -> None:
    accent = f" style='border-top:2px solid var(--{tone});'" if tone else ""
    st.markdown(
        f'<div class="surface-tight"{accent}><div class="section-label">{label}</div><div class="confidence-value">{value}</div><div class="metric-context">{context}</div></div>',
        unsafe_allow_html=True,
    )


def prediction_grid(prediction: Any) -> None:
    values = [
        ("Category", prediction.category.title()),
        ("Priority", prediction.priority.title()),
        ("Queue", prediction.queue),
        ("Sentiment", prediction.sentiment.title()),
    ]
    columns = st.columns(4)
    for column, (label, value) in zip(columns, values):
        with column:
            st.markdown(
                f'<div class="surface-tight"><div class="section-label">{label}</div><div style="font-family:inherit;font-size:1.15rem;font-weight:600;min-height:1.7rem">{value}</div></div>',
                unsafe_allow_html=True,
            )


def review_panel(
    human_review: bool, confidence: float, threshold: float, explanation: str
) -> None:
    status = "HUMAN REVIEW REQUIRED" if human_review else "AUTO-ROUTED"
    tone = "review" if human_review else "auto"
    st.markdown(
        f'<div class="{tone}"><strong>{status}</strong><br>{explanation}</div>',
        unsafe_allow_html=True,
    )
    columns = st.columns([1, 2])
    with columns[0]:
        confidence_bar(confidence, threshold)
    with columns[1]:
        st.markdown(f"**Threshold:** {threshold:.0%}")
        st.caption(
            "Confidence is the mean calibrated probability across category, priority, queue, and sentiment models. A policy can still require review independently."
        )


def empty_state(title: str, detail: str) -> None:
    st.markdown(
        f'<div class="empty-state"><strong>{title}</strong><br><span>{detail}</span></div>',
        unsafe_allow_html=True,
    )


def activity_feed(events: list[dict[str, Any]]) -> None:
    if not events:
        empty_state(
            "No live activity yet",
            "Analyze a new ticket to start building an operational activity trail.",
        )
        return
    for event in events[:6]:
        stamp = event.get("timestamp", "")
        try:
            time = datetime.fromisoformat(stamp).strftime("%H:%M")
        except ValueError:
            time = "--:--"
        status = {
            "review_required": "awaiting human review",
            "reviewed": "reviewed by an agent",
            "auto_routed": "auto-routed",
        }.get(event.get("status"), "status unavailable")
        st.markdown(
            f'<div class="activity-row"><span class="activity-time">{time}</span><br><strong>Ticket analyzed</strong><br><span class="metric-context">{event.get("category", "Unknown").title()} · {event.get("priority", event.get("urgency", "unknown")).title()} · {status}</span></div>',
            unsafe_allow_html=True,
        )


def workflow(active: int) -> None:
    labels = ["Upload CSV", "Validate", "Analyze", "Review", "Download"]
    html = (
        '<div class="workflow">'
        + "".join(
            f'<div class="workflow-step {"active" if index <= active else ""}">{index + 1:02d} &nbsp; {label}</div>'
            for index, label in enumerate(labels)
        )
        + "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
