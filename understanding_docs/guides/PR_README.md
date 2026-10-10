# Relay Partner Guide

Welcome! This folder is a beginner guide for the person helping with
the Relay project. You do not need to know artificial intelligence, machine
learning, Python, or Streamlit before starting.

## What is this project?

Relay is a support-ticket assistant. A customer writes a support ticket, and
Relay predicts:

- What kind of problem it is
- How urgent it may be
- Which support queue should receive it
- Whether the writing sounds positive or negative
- How confident the models are

Relay then applies separate business rules. The result is either:

1. **Auto-routed**: confidence and policy checks are acceptable.
2. **Review required**: a human must check the recommendation.
3. **Reviewed**: a human has actually completed that check.

Relay is decision support. It is not a replacement for support agents.

## The one-minute mental model

```text
Ticket
  -> ML prediction
  -> Business rules
  -> Final routing decision
  -> Human review when necessary
```

## Read in this order

1. Read [RUNNING.md](./RUNNING.md).
2. Read [PROJECT_MAP.md](./PROJECT_MAP.md) to understand every important folder.
3. Use [DEMO.md](./DEMO.md) for a clean demonstration.
4. Use [PRESENTATION.md](./PRESENTATION.md) before presenting.

## Important folders

| Folder/file                  | What it contains                             |
| ---------------------------- | -------------------------------------------- |
| `app.py`                     | Streamlit UI                                 |
| `api.py`                     | FastAPI API                                  |
| `relay/`                     | Prediction, policy, data, and shared UI code |
| `models/`                    | Saved trained models                         |
| `config/business_rules.json` | Business rules                               |
| `tests/`                     | Automated tests                              |
| `reports/`                   | Real evaluation metrics and charts           |

The **Business Rules** page is needed because policies are organization
decisions, not things the ML model should learn secretly. It controls the
confidence threshold, payment priority override, security review requirement,
and billing queue override. The old Settings page was removed because it
duplicated the threshold control and its default queue field was not used by
the application.

The public project documentation is in the root [README.md](../README.md) and
[docs/](../docs/).
