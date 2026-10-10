# Modeling Decisions

## Intake Text

The supervised models receive one field only: `text = subject + " " + body`. This mirrors what is available when a new ticket arrives.

## Data Leakage Prevention

The public support dataset includes fields that are unavailable at ticket intake or can reveal the answer after resolution. The training features explicitly exclude `answer`, resolution details, assigned teams, resolution time, customer satisfaction after resolution, and other post-resolution fields. The `answer` column is never passed to a vectorizer. Targets are the labeled `type`, `priority`, and `queue` columns.

The raw dataset remains under `data/raw/` for provenance, while `clean_support_tickets()` constructs the restricted modeling frame.

## Algorithms

Each target has two candidate models: TF-IDF with Logistic Regression and TF-IDF with LinearSVC. Both use word unigrams and bigrams, a capped vocabulary, accent stripping, and class weighting. The winner is selected using macro F1 on the held-out test set. The persisted LinearSVC pipeline is calibrated with `CalibratedClassifierCV` so inference confidence is a probability-like calibrated class estimate rather than an arbitrary decision score.

Sentiment is a separate model trained on the public `SetFit/sst2` dataset. Sentiment labels are not fabricated from support tickets.

## Evaluation

The split is 80% training and 20% testing with `random_state=42` and target stratification. The test partition is never used to fit the saved artifacts. Accuracy, macro F1, weighted F1, precision, recall, classification reports, and confusion matrices are written under `reports/`.

## Human Review

The model confidence is not a guarantee of correctness. The app averages the four calibrated class probabilities and uses a configurable 0.50 default threshold. Predictions below it, and tickets matched by review policies, require human review. The threshold is a business operating point, not a claim that 50% means 50% real-world accuracy.

## Business Rules

Business instructions live in `config/business_rules.json` and are applied after ML inference. They can override priority, queue, and review status, but never modify or retrain a model. The UI displays both the raw ML prediction and the final policy decision.
