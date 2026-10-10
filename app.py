from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from relay.policy import apply_policy, load_policy, save_policy
from relay.predictor import MODEL_DIR, Predictor
from relay.ui.components import (
    activity_feed,
    badge,
    brand,
    confidence_bar,
    empty_state,
    metric_card,
    page_header,
    prediction_grid,
    review_panel,
    section_header,
    workflow,
)
from relay.ui.styles import inject_styles

st.set_page_config(
    page_title="Relay · Support Intelligence",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

LOG_PATH = Path("triage_logs.jsonl")


@st.cache_resource
def get_predictor() -> Predictor:
    return Predictor()


@st.cache_data(show_spinner=False)
def get_metrics() -> dict[str, Any]:
    path = Path("reports/metrics.json")
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


@st.cache_data(show_spinner=False)
def get_events() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
            event.setdefault(
                "confidence",
                min(
                    float(event.get("category_confidence", 0)),
                    float(event.get("urgency_confidence", 0)),
                ),
            )
            event.setdefault("priority", event.get("urgency", "unknown"))
            event.setdefault("queue", event.get("route", "Unassigned"))
            event.setdefault("final_priority", event.get("priority", "unknown"))
            event.setdefault("final_queue", event.get("queue", "Unassigned"))
            event.setdefault(
                "status",
                (
                    "review_required"
                    if event.get("needs_review", False)
                    else "auto_routed"
                ),
            )
            event.setdefault("policy_override", False)
            events.append(event)
        except json.JSONDecodeError:
            continue
    return list(reversed(events))


def log_event(text: str, prediction: Any, decision: Any) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": text,
        "category": prediction.category,
        "priority": prediction.priority,
        "queue": prediction.queue,
        "sentiment": prediction.sentiment,
        "confidence": prediction.confidence,
        "needs_review": decision.human_review,
        "final_priority": decision.priority,
        "final_queue": decision.queue,
        "status": "review_required" if decision.human_review else "auto_routed",
        "policy_override": decision.priority != prediction.priority
        or decision.queue != prediction.queue,
        "policy_explanation": decision.explanation,
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    get_events.clear()


def update_event_status(
    timestamp: str,
    *,
    category: str,
    priority: str,
    queue: str,
) -> None:
    if not LOG_PATH.exists():
        return
    updated_lines: list[str] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("timestamp") == timestamp:
            event["status"] = "reviewed"
            event["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            event["review_action"] = "human_review"
            event["category"] = category
            event["final_category"] = category
            event["final_priority"] = priority
            event["final_queue"] = queue
        updated_lines.append(json.dumps(event))
    LOG_PATH.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    get_events.clear()


def navigation() -> str:
    with st.sidebar:
        brand()
        st.caption("Ticket routing workspace")

    sections = {
        "Overview": ["Dashboard"],
        "Tickets": ["New Ticket", "Ticket Queue", "Batch Analysis"],
        "Intelligence": ["Analytics", "Models"],
        "Configuration": ["Business Rules"],
    }
    page_to_section = {
        page: section for section, pages in sections.items() for page in pages
    }

    def select_section(section: str) -> None:
        st.session_state["active_section"] = section
        st.session_state["active_page"] = sections[section][0]

    active_page = st.session_state.setdefault("active_page", "Dashboard")
    active_section = st.session_state.setdefault(
        "active_section", page_to_section.get(active_page, "Overview")
    )
    section_names = list(sections)
    section_columns = st.columns(4)
    for column, section in zip(section_columns, section_names):
        with column:
            if st.button(
                section,
                key=f"section_{section.lower()}",
                type="primary" if section == active_section else "secondary",
                use_container_width=True,
            ):
                select_section(section)
                st.rerun()

    pages = sections[active_section]
    if len(pages) > 1:
        page_columns = st.columns(len(pages))
        for column, page in zip(page_columns, pages):
            with column:
                if st.button(
                    page,
                    key=f"page_{page.lower().replace(' ', '_')}",
                    type="primary" if page == active_page else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["active_page"] = page
                    st.session_state["active_section"] = page_to_section[page]
                    st.rerun()
    st.divider()
    return st.session_state["active_page"]


def render_dashboard() -> None:
    events = get_events()
    page_header(
        "Support Intelligence",
        "Monitor ticket decisions, model confidence, and human-review workload.",
    )
    processed = len(events)
    reviews = sum(event.get("status") == "review_required" for event in events)
    auto = sum(event.get("status") == "auto_routed" for event in events)
    high_priority = sum(
        str(event.get("final_priority", event.get("priority", ""))).lower()
        in {"high", "critical"}
        for event in events
    )
    avg_confidence = (
        sum(float(event.get("confidence", 0)) for event in events) / processed
        if processed
        else 0
    )
    columns = st.columns(5)
    with columns[0]:
        metric_card("Processed tickets", f"{processed:,}", "Live event log", "accent")
    with columns[1]:
        metric_card(
            "Auto-routed",
            f"{auto:,}",
            (
                f"{auto / processed:.1%} of live tickets"
                if processed
                else "No live tickets yet"
            ),
            "success",
        )
    with columns[2]:
        metric_card("Human review", f"{reviews:,}", "Needs agent attention", "warning")
    with columns[3]:
        metric_card(
            "High priority",
            f"{high_priority:,}",
            "High or critical live tickets",
            "warning",
        )
    with columns[4]:
        metric_card(
            "Average confidence",
            f"{avg_confidence:.0%}",
            "Across live predictions" if processed else "No live predictions yet",
            "accent",
        )
    st.caption("Live event log · counts reflect tickets analyzed in this workspace")

    left, right = st.columns([1.5, 1], gap="large")
    with left:
        section_header("Ticket volume", "Live tickets analyzed in this workspace")
        if events:
            raw = pd.DataFrame(events)
            st.bar_chart(
                raw["category"].fillna("Unlabeled").value_counts(),
                height=280,
                color="#1f6f64",
            )
        else:
            empty_state(
                "No live ticket volume yet",
                "Analyze a new ticket to populate the operational overview.",
            )
    with right:
        section_header("Human review queue", "Live tickets below policy threshold")
        review_events = [
            event for event in events if event.get("status") == "review_required"
        ]
        if not review_events:
            empty_state(
                "No tickets require review",
                "All current live tickets have been automatically routed.",
            )
        else:
            for event in review_events[:4]:
                confidence = float(event.get("confidence", 0))
                st.markdown(
                    f"<div class='activity-row'><strong>{event.get('category', 'Unknown').title()}</strong> {badge('REVIEW', 'warning')}<br><span class='metric-context'>{event.get('text', '')[:72]}</span><br><span class='metric-context'>Confidence {confidence:.0%} · {event.get('queue', 'Unassigned')}</span></div>",
                    unsafe_allow_html=True,
                )
            st.button(
                "Open Review Queue",
                key="dashboard_review",
                on_click=lambda: st.session_state.update(
                    active_page="Ticket Queue", active_section="Tickets"
                ),
            )
    st.divider()
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        section_header(
            "Recent activity", "Events recorded by the live inference workflow"
        )
        activity_feed(events)
    with right:
        section_header("Recent tickets", "Latest live routing decisions")
        if events:
            recent = pd.DataFrame(events[:6])
            recent["Ticket"] = recent["text"].fillna("").str.slice(0, 52)
            recent["Priority"] = recent["final_priority"].fillna("").str.title()
            recent["Queue"] = recent["final_queue"].fillna("")
            recent["Status"] = recent["status"].map(
                {
                    "auto_routed": "Auto-routed",
                    "review_required": "Review required",
                    "reviewed": "Reviewed",
                }
            )
            st.dataframe(
                recent[["Ticket", "Priority", "Queue", "Status"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            empty_state("No recent tickets", "New live decisions will appear here.")


def render_triage(predictor: Predictor, policy: dict[str, Any]) -> None:
    page_header(
        "New Ticket", "Analyze an incoming support request and determine its routing."
    )
    workflow(2)
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        section_header(
            "Ticket details",
            "Only subject and description are sent to the saved models.",
        )
        examples = {
            "Start with a blank ticket": ("", ""),
            "Double payment · demo": (
                "Double payment",
                "I was charged twice for my monthly subscription and need the second payment refunded.",
            ),
            "Account access · demo": (
                "Cannot access account",
                "My account is locked after multiple login attempts and I urgently need access.",
            ),
            "Product question · demo": (
                "Product information",
                "Can you tell me whether the annual subscription includes premium support?",
            ),
        }
        if "ticket_subject" not in st.session_state:
            (
                st.session_state["ticket_subject"],
                st.session_state["ticket_description"],
            ) = examples["Start with a blank ticket"]

        def load_example() -> None:
            selected_example = st.session_state.get(
                "ticket_example", "Start with a blank ticket"
            )
            example_subject, example_description = examples[selected_example]
            st.session_state["ticket_subject"] = example_subject
            st.session_state["ticket_description"] = example_description

        st.selectbox(
            "Load an unseen example",
            list(examples),
            key="ticket_example",
            on_change=load_example,
        )
        subject = st.text_input(
            "Subject",
            key="ticket_subject",
            placeholder="Short summary of the issue",
        )
        description = st.text_area(
            "Description",
            key="ticket_description",
            height=175,
            placeholder="Describe the customer's issue in their own words.",
        )
        analyze = st.button("Analyze Ticket", type="primary")
    with right:
        if analyze:
            try:
                text = f"{subject} {description}".strip()
                prediction = predictor.predict_ticket(text)
                decision = apply_policy(text, prediction, policy)
                log_event(text, prediction, decision)
                st.subheader("Triage result")
                prediction_grid(prediction)
                section_header("Final routing decision")
                review_panel(
                    decision.human_review,
                    prediction.confidence,
                    float(policy.get("confidence_threshold", 0.5)),
                    decision.explanation,
                )
                st.markdown(
                    f"**Priority:** {decision.priority.title()}  \n**Queue:** {decision.queue}"
                )
            except ValueError as error:
                st.error(f"Unable to analyze this ticket\n\n{error}")
        else:
            empty_state(
                "Ready for analysis",
                "Enter a subject and description, then analyze the ticket with the saved models.",
            )


def render_queue() -> None:
    page_header(
        "Ticket Queue", "Review live inference events and their final routing status."
    )
    events = get_events()
    if not events:
        empty_state(
            "No tickets in the live queue",
            "Analyze a new ticket to create the first queue event.",
        )
        return
    frame = pd.DataFrame(events)
    frame["ticket"] = frame["text"].fillna("").str.slice(0, 70)
    status_labels = {
        "auto_routed": "Auto-routed",
        "review_required": "Review required",
        "reviewed": "Reviewed",
    }
    frame["status"] = frame["status"].map(status_labels).fillna("Unknown")
    frame["confidence"] = frame["confidence"].map(lambda value: f"{float(value):.0%}")
    search = st.text_input(
        "Search tickets", placeholder="Search text, category, or queue"
    )
    status_filter = st.selectbox(
        "Filter status", ["All", "Auto-routed", "Review required", "Reviewed"]
    )
    if search:
        mask = (
            frame.astype(str)
            .apply(lambda column: column.str.contains(search, case=False, na=False))
            .any(axis=1)
        )
        frame = frame[mask]
    if status_filter != "All":
        frame = frame[frame["status"] == status_filter]
    columns = [
        "ticket",
        "category",
        "final_priority",
        "final_queue",
        "sentiment",
        "confidence",
        "status",
        "timestamp",
    ]
    display = frame.reindex(columns=columns).rename(
        columns={
            "ticket": "Ticket",
            "category": "Category",
            "final_priority": "Priority",
            "final_queue": "Queue",
            "sentiment": "Sentiment",
            "confidence": "Confidence",
            "status": "Status",
            "timestamp": "Created",
        }
    )
    display["Action"] = display["Status"].map(
        {
            "Auto-routed": "Routed",
            "Review required": "Review",
            "Reviewed": "Completed",
        }
    )
    display = display[
        [
            "Ticket",
            "Category",
            "Priority",
            "Queue",
            "Sentiment",
            "Status",
            "Created",
            "Action",
        ]
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(display):,} live event(s).")
    reviewable = frame[frame["status"] == "Review required"]
    if not reviewable.empty:
        st.subheader("Review action")
        choices = {
            f"{row.ticket} · {row.category.title()} · {row.timestamp}": row
            for row in reviewable.itertuples()
        }
        selected_label = st.selectbox("Ticket requiring review", list(choices))
        selected = choices[selected_label]
        columns = st.columns(3)
        with columns[0]:
            category = st.text_input("Final category", value=str(selected.category))
        with columns[1]:
            priority = st.selectbox(
                "Final priority",
                ["low", "medium", "high", "critical"],
                index=(
                    ["low", "medium", "high", "critical"].index(
                        str(selected.final_priority).lower()
                    )
                    if str(selected.final_priority).lower()
                    in {"low", "medium", "high", "critical"}
                    else 1
                ),
            )
        with columns[2]:
            queue = st.text_input("Final queue", value=str(selected.final_queue))
        if st.button("Complete human review", type="primary"):
            update_event_status(
                choices[selected_label].timestamp,
                category=category.strip() or str(selected.category),
                priority=priority,
                queue=queue.strip() or str(selected.final_queue),
            )
            st.success("Ticket marked as reviewed.")
            st.rerun()


def render_batch(predictor: Predictor, policy: dict[str, Any]) -> None:
    page_header(
        "Batch Analysis",
        "Process a CSV of incoming tickets through the saved models and policy layer.",
    )
    workflow(0 if "batch_results" not in st.session_state else 4)
    uploaded = st.file_uploader(
        "Upload CSV", type="csv", help="Required columns: subject, description"
    )
    if not uploaded:
        section_header("CSV format")
        st.code(
            "subject,description\nDouble payment,I was charged twice for my subscription\nAccount access,My login is locked",
            language="csv",
        )
        st.caption(
            "Demo tickets are unseen examples created for application demonstration."
        )
        return
    try:
        batch = pd.read_csv(io.BytesIO(uploaded.getvalue()))
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
        workflow(1)
        st.error(f"Unable to read this CSV: {error}")
        return
    required = {"subject", "description"}
    missing = required - set(batch.columns)
    if missing:
        workflow(1)
        st.error(
            f"Unable to validate this file. Missing columns: {', '.join(sorted(missing))}."
        )
        return
    if batch.empty:
        workflow(1)
        st.error("Unable to analyze this file. The CSV contains no tickets.")
        return
    if (
        batch[["subject", "description"]]
        .fillna("")
        .astype(str)
        .apply(lambda column: column.str.strip())
        .eq("")
        .all(axis=1)
        .any()
    ):
        workflow(1)
        st.error("Every ticket must include a subject or description.")
        return
    workflow(2)
    if st.button("Analyze CSV", type="primary"):
        with st.spinner("Running saved models across the uploaded tickets..."):
            try:
                results = predictor.predict_frame(batch)
            except ValueError as error:
                st.error(f"Unable to analyze this file: {error}")
                return
            results = results.drop(columns=["confidence_basis"], errors="ignore")
            decisions = []
            predictions = []
            for row in batch.itertuples(index=False):
                text = f"{row.subject} {row.description}"
                prediction = predictor.predict_ticket(text)
                predictions.append(prediction)
                decisions.append(apply_policy(text, prediction, policy))
            results["final_priority"] = [decision.priority for decision in decisions]
            results["final_queue"] = [decision.queue for decision in decisions]
            results["human_review"] = [decision.human_review for decision in decisions]
            results["routing_status"] = [
                "review_required" if decision.human_review else "auto_routed"
                for decision in decisions
            ]
            results["review_reason"] = [
                decision.explanation if decision.human_review else ""
                for decision in decisions
            ]
            results["policy_override"] = [
                decision.priority != prediction.priority
                or decision.queue != prediction.queue
                for decision, prediction in zip(decisions, predictions)
            ]
            results["policy_explanation"] = [
                decision.explanation for decision in decisions
            ]
            st.session_state["batch_results"] = results
            st.toast("CSV processed successfully.")
    if "batch_results" in st.session_state:
        results = st.session_state["batch_results"]
        workflow(4)
        review_count = int(results["human_review"].sum())
        columns = st.columns(3)
        columns[0].metric("Tickets analyzed", f"{len(results):,}")
        columns[1].metric("Auto-routed", f"{len(results) - review_count:,}")
        columns[2].metric("Human review", f"{review_count:,}")
        st.dataframe(
            results.drop(columns=["text"], errors="ignore"),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download predictions",
            results.to_csv(index=False),
            "relay_triage_predictions.csv",
            "text/csv",
        )


def render_analytics() -> None:
    page_header(
        "Analytics",
        "Understand ticket volume, routing outcomes, and review workload.",
    )
    events = get_events()
    live = pd.DataFrame(events)
    if live.empty:
        empty_state(
            "No analytics yet",
            "Analyze a ticket or process a batch to populate operational analytics.",
        )
        return
    left, right = st.columns(2, gap="large")
    with left:
        section_header("Tickets by category", "Live analyzed tickets")
        st.bar_chart(live["category"].value_counts(), color="#1f6f64")
    with right:
        section_header("Priority distribution", "Final routed priority")
        st.bar_chart(live["final_priority"].value_counts(), color="#b45309")
    left, right = st.columns(2, gap="large")
    with left:
        section_header("Queue distribution", "Final routed queue")
        st.bar_chart(live["final_queue"].value_counts().head(10), color="#78716c")
    with right:
        section_header("Routing outcomes", "Live ticket status")
        st.bar_chart(
            live["status"]
            .map(
                {
                    "auto_routed": "Auto-routed",
                    "review_required": "Review required",
                    "reviewed": "Reviewed",
                }
            )
            .value_counts(),
            color="#1f6f64",
        )
    st.metric("Average confidence", f"{live['confidence'].astype(float).mean():.0%}")
    st.caption(
        f"Policy overrides: {int(live['policy_override'].fillna(False).sum())} · "
        f"Review rate: {(live['status'].isin(['review_required', 'reviewed'])).mean():.1%}"
    )


def render_models() -> None:
    page_header(
        "Model Performance",
        "Inspect the classifiers, held-out metrics, and evaluation artifacts.",
    )
    metrics = get_metrics()
    dataset = metrics.get("dataset", {})
    columns = st.columns(4)
    columns[0].metric("Training records", f"{dataset.get('rows_after_cleaning', 0):,}")
    columns[1].metric("Features", "TF-IDF")
    columns[2].metric("Test split", "20%")
    columns[3].metric("Random state", "42")
    model_results = {
        **metrics.get("targets", {}),
        "sentiment": metrics.get("sentiment", {}),
    }
    for target, details in model_results.items():
        values = details["test_metrics"]
        st.markdown(f"### {target.title()} Classifier")
        st.caption(
            f"Selected candidate: {details['selected_model']} · {details['test_rows']:,} unseen test rows"
        )
        columns = st.columns(5)
        for column, metric in zip(
            columns, ("accuracy", "macro_f1", "weighted_f1", "precision", "recall")
        ):
            column.metric(metric.replace("_", " ").title(), f"{values[metric]:.1%}")
    st.subheader("Confusion matrices")
    for target in ("category", "priority", "queue"):
        image = Path("reports/figures") / f"{target}_confusion_matrix.png"
        if image.exists():
            st.image(str(image), caption=f"{target.title()} · unseen test set")
    section_header("Model info")
    info = pd.DataFrame(
        {
            "Field": ["Model version", "Features", "Classifier", "Dataset", "Status"],
            "Value": [
                "1.0.0",
                "TF-IDF word n-grams",
                "Selected Logistic Regression or calibrated LinearSVC",
                "Prady06/customer-support-tickets",
                "Loaded",
            ],
        }
    )
    st.dataframe(info, use_container_width=True, hide_index=True)


def render_rules(predictor: Predictor, policy: dict[str, Any]) -> None:
    page_header(
        "Business Rules",
        "Define policies that refine automated routing decisions without changing the trained models.",
    )
    st.caption(
        "Rules are applied after ML inference and remain auditable in config/business_rules.json."
    )
    for rule in policy.get("keyword_priority_overrides", []):
        tone = "success" if rule.get("enabled", True) else "neutral"
        state = "ENABLED" if rule.get("enabled", True) else "DISABLED"
        st.markdown(
            f"<div class='surface-tight' style='margin:.5rem 0'><strong>Payment and refund signals</strong><br><span class='metric-context'>Condition: {', '.join(rule.get('keywords', []))} · Action: Priority → {rule.get('priority', 'high').title()}</span><span style='float:right'>{badge(state, tone)}</span></div>",
            unsafe_allow_html=True,
        )
    for category in policy.get("mandatory_review_categories", []):
        st.markdown(
            f"<div class='surface-tight' style='margin:.5rem 0'><strong>{category.title()} issues</strong><br><span class='metric-context'>Condition: Category = {category} · Action: Require human review</span><span style='float:right'>{badge('ENABLED', 'success')}</span></div>",
            unsafe_allow_html=True,
        )
    for rule in policy.get("keyword_review_overrides", []):
        tone = "success" if rule.get("enabled", True) else "neutral"
        state = "ENABLED" if rule.get("enabled", True) else "DISABLED"
        st.markdown(
            f"<div class='surface-tight' style='margin:.5rem 0'><strong>Keyword review</strong><br><span class='metric-context'>Condition: {', '.join(rule.get('keywords', []))} · Action: Require human review</span><span style='float:right'>{badge(state, tone)}</span></div>",
            unsafe_allow_html=True,
        )
    for rule in policy.get("queue_overrides", []):
        st.markdown(
            f"<div class='surface-tight' style='margin:.5rem 0'><strong>{rule.get('category', 'Category').title()} queue</strong><br><span class='metric-context'>Condition: Category = {rule.get('category')} · Action: Queue → {rule.get('queue')}</span><span style='float:right'>{badge('ENABLED', 'success')}</span></div>",
            unsafe_allow_html=True,
        )
    st.divider()
    section_header(
        "Add or edit a rule",
        "Use plain business language; the rule is stored as structured JSON.",
    )
    threshold = st.slider(
        "Confidence threshold",
        0.50,
        0.99,
        float(policy.get("confidence_threshold", 0.50)),
        0.01,
    )
    cols = st.columns(2)
    with cols[0]:
        rule_name = st.text_input("Rule name", placeholder="Enterprise customers")
        condition_category = st.selectbox(
            "Condition category",
            ["None"]
            + sorted(str(value) for value in predictor.models["category"].classes_),
        )
    with cols[1]:
        action = st.selectbox(
            "Action", ["Require human review", "Set priority", "Override queue"]
        )
        action_value = st.text_input(
            "Action value", placeholder="High or Enterprise Support"
        )
    enabled = st.toggle("Enabled", value=True)
    if st.button("Save Rule", type="primary"):
        updated = dict(policy)
        updated["confidence_threshold"] = threshold
        if enabled and condition_category != "None" and rule_name:
            if action == "Require human review":
                updated["mandatory_review_categories"] = sorted(
                    set(
                        updated.get("mandatory_review_categories", [])
                        + [condition_category]
                    )
                )
            elif action == "Set priority":
                updated["category_priority_overrides"] = updated.get(
                    "category_priority_overrides", []
                ) + [
                    {
                        "category": condition_category,
                        "priority": action_value.lower(),
                        "description": rule_name,
                        "enabled": True,
                    }
                ]
            else:
                updated["queue_overrides"] = updated.get("queue_overrides", []) + [
                    {
                        "category": condition_category,
                        "queue": action_value,
                        "description": rule_name,
                        "enabled": True,
                    }
                ]
            save_policy(updated)
            st.toast("Business rule saved.")
            st.rerun()
        else:
            st.warning(
                "Provide a rule name, choose a category, and enable the rule before saving."
            )


try:
    predictor = get_predictor()
except FileNotFoundError as error:
    st.error("Unable to load the saved model artifacts.")
    st.code("python scripts/download_dataset.py\npython scripts/train.py")
    st.warning(str(error))
    st.stop()

page = navigation()
policy = load_policy()

if page == "Dashboard":
    render_dashboard()
elif page == "New Ticket":
    render_triage(predictor, policy)
elif page == "Ticket Queue":
    render_queue()
elif page == "Batch Analysis":
    render_batch(predictor, policy)
elif page == "Analytics":
    render_analytics()
elif page == "Models":
    render_models()
elif page == "Business Rules":
    render_rules(predictor, policy)
