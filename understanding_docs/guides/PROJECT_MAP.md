# Relay Project Map

This page explains what each important folder and file does. You do not need
to open every file to run the project.

## Main application files

| Path                     | Purpose                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------- |
| `app.py`                 | Streamlit pages, buttons, forms, live ticket log, and review workflow                 |
| `api.py`                 | Small FastAPI service with health and prediction endpoints                            |
| `requirements.txt`       | Python packages needed by the application and tests                                   |
| `pyproject.toml`         | Python tool and project metadata                                                      |
| `.streamlit/config.toml` | Streamlit dark-theme defaults                                                         |
| `.gitignore`             | Prevents secrets, caches, datasets, models, logs, and build files from being uploaded |

## ML and policy code

| Path                         | Purpose                                                                          |
| ---------------------------- | -------------------------------------------------------------------------------- |
| `relay/predictor.py`         | Loads saved joblib models and performs inference; it never trains during app use |
| `relay/policy.py`            | Applies business rules after the model prediction                                |
| `relay/data.py`              | Shared dataset cleaning and preparation helpers                                  |
| `relay/ui/components.py`     | Reusable cards, badges, tables, metrics, and review components                   |
| `relay/ui/styles.py`         | One dark visual system: Google Sans, black surfaces, yellow and green accents    |
| `config/business_rules.json` | Editable policy settings used after ML inference                                 |

## Data, models, and reports

| Path                   | Purpose                                                                          |
| ---------------------- | -------------------------------------------------------------------------------- |
| `data/raw/`            | Downloaded CSV datasets; ignored by Git and recreated by the download script     |
| `models/`              | Trained `.joblib` pipelines; ignored by Git because they are generated artifacts |
| `reports/metrics.json` | Held-out evaluation metrics shown in Model Performance                           |
| `reports/figures/`     | Generated confusion matrices and evaluation images                               |
| `notebooks/`           | Optional data exploration notebook; not needed to run the application            |

## Training scripts

| Path                          | Purpose                                                                 |
| ----------------------------- | ----------------------------------------------------------------------- |
| `scripts/download_dataset.py` | Downloads the public datasets                                           |
| `scripts/explore_dataset.py`  | Prints dataset columns, missing values, and label distributions         |
| `scripts/train.py`            | Compares models, evaluates them on held-out data, and saves the winners |

Training is only needed for a fresh clone or when rebuilding model artifacts.
The normal demo uses the already-created artifacts.

## Tests and documentation

| Path                           | Purpose                                                       |
| ------------------------------ | ------------------------------------------------------------- |
| `tests/test_predictor.py`      | Model, policy, confidence, review, and batch validation tests |
| `tests/test_api.py`            | API health and invalid-request tests                          |
| `docs/MODEL_CARD.md`           | Model scope, metrics, risks, and responsible use              |
| `docs/MODELING_DECISIONS.md`   | Feature choices and leakage prevention                        |
| `docs/ACADEMIC_EXPLANATION.md` | Longer explanation for academic review                        |
| `docs/guides/`                 | Beginner setup, demo, presentation, and this project map      |

## The complete data flow

```text
Customer ticket
  -> subject + description
  -> saved ML models
  -> category, priority, queue, sentiment, confidence
  -> business rules
  -> auto-routed or review required
  -> reviewed only after a person saves a review
```

The model does not use answers, agents, resolution status, or other
post-resolution information. Those fields would leak future information into
the prediction.

## What should not be uploaded to GitHub

Do not upload:

- `.env` files, API keys, passwords, or Streamlit secrets
- `.venv/`
- Python caches and test caches
- downloaded CSV files under `data/raw/`
- generated `.joblib` files under `models/`
- runtime logs such as `triage_logs.jsonl`
- local databases, coverage output, build output, or temporary files

The root `.gitignore` contains these protections. Always inspect
`git status` before committing.
