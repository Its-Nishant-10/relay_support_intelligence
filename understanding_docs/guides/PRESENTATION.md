# Relay Presentation

## One-sentence description

Relay is a supervised NLP support-ticket triage system that predicts category,
priority, queue, and sentiment, then applies auditable business rules and
human review.

## Problem statement

Support teams need a faster and more consistent first decision about where
incoming tickets should go, without removing human control from uncertain or
high-impact cases.

## Methodology

1. Download a public synthetic support-ticket dataset.
2. Keep only intake-time subject and body text.
3. Clean and deduplicate the text.
4. Split the data into stratified training and test sets.
5. Convert text into TF-IDF word features.
6. Compare Logistic Regression and LinearSVC.
7. Select the candidate with the best held-out macro F1.
8. Save the model pipeline.
9. Apply business rules after prediction.
10. Require human review when policy or confidence requires it.

## Honest results

The current held-out macro F1 values are approximately:

- Category: 0.850
- Priority: 0.569
- Queue: 0.539
- Sentiment: 0.779

Do not claim production accuracy, real customer data, enterprise scale, or
autonomous decision-making.

## Strong answers to common questions

### Why not use a chatbot?

The project needs repeatable classification and auditable routing. A
supervised model is easier to evaluate against labeled outcomes and can run
without an API key.

### Why have business rules?

Some decisions are organizational policies rather than patterns learned from
historical text. Keeping them separate makes them visible and editable.

### Why keep human review?

Synthetic training data and domain changes can produce confident mistakes.
Human review protects important workflows and keeps the system as decision
support.

### What is the main limitation?

The dataset is synthetic, and priority and queue performance are lower than
category performance. A real organization would need representative
validation data and monitoring before deployment.

## Final sentence

> "The important design choice is not just the prediction; it is the complete
> ML-to-policy-to-routing workflow with an explicit human exception path."

## Suggested slide order

1. Problem
2. Solution
3. Architecture
4. Dataset
5. ML approach
6. Business rules
7. Human review
8. UI
9. Results
10. Demo
11. Limitations
12. Conclusion
