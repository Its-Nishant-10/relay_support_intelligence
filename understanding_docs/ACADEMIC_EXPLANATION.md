# Academic Explanation

## Why TF-IDF?

TF-IDF is a strong, transparent baseline for ticket text. It emphasizes terms that matter within a ticket while down-weighting words that occur across the whole corpus. Word unigrams and bigrams capture both individual terms and useful phrases, while sparse features keep training and inference inexpensive.

## Why supervised classification?

The dataset provides labeled outcomes at intake: type, priority, and queue. Supervised classification learns relationships between intake text and those labels from examples. This is different from a keyword lookup because the learned decision boundary is estimated from the training records and evaluated on unseen records.

## Why separate models?

Category, priority, queue, and sentiment are different prediction targets with different label spaces and error costs. Separate pipelines prevent one target from being hardcoded from another and allow each target to select its own best candidate model.

## Why a train/test split?

A final test partition approximates future tickets the model has never seen. Keeping it out of fitting prevents optimistic evaluation. This project uses an 80/20 stratified split with a fixed random seed for reproducibility.

## Why macro F1?

Accuracy can hide poor performance on minority classes. Macro F1 gives every class equal weight, which matters for queues and priorities with uneven frequency. Weighted F1, precision, recall, and accuracy are also reported to show complementary views.

## Why confidence thresholds?

A prediction should not be treated as equally reliable for every ticket. Calibrated class probabilities provide a model-derived confidence signal. The application averages the four model probabilities and routes tickets below the configurable threshold to a human. The threshold is a business operating point and must be validated against routing costs.

## Why human-in-the-loop?

Synthetic training data and domain shift can produce confident errors. Human review protects high-impact workflows and creates a future source of corrected labels. The policy layer can require review independently of confidence for selected categories.

## Why keep business rules separate from ML?

Business instructions such as "refunds are high priority" are policy decisions, not evidence learned from the training corpus. Keeping them in a JSON policy layer makes overrides auditable, editable, and reversible without changing model artifacts. The UI displays both the raw ML prediction and the final policy decision.

## Why leakage is dangerous?

Fields such as an answer, resolution status, assigned team, or resolution time can reveal the outcome after the ticket is handled. If those fields are used during training, test results look strong but the model cannot reproduce the same signal when a new ticket arrives. This project uses only subject and body for all support-target models.

## Why can the model fail on unseen domains?

The public dataset is synthetic and its vocabulary, language balance, taxonomy, and writing style may not match a real organization. New products, rare incidents, multilingual tickets, and policy changes can shift the data distribution. Production use would require anonymized historical validation, drift monitoring, recalibration, and agent feedback.
