# Relay Demo

This script is designed for a smooth five-to-ten-minute demonstration.

## 1. Overview

Say:

> "This page shows what is happening with tickets analyzed in the current
> workspace. Empty counts are real; Relay does not invent operational data."

Point out the top navigation: Overview, Tickets, Intelligence, and
Configuration.

## 2. Auto-routed ticket

Open **Tickets -> New Ticket**.

Use:

- Subject: `Double payment`
- Description: `I was charged twice for my monthly subscription and need the second payment refunded.`

Click **Analyze Ticket**.

Explain:

> "The model produced the category, priority, queue, sentiment, and confidence.
> The payment policy then raised the priority to high. Because the final checks
> passed, the ticket is auto-routed."

## 3. Review-required ticket

Submit:

- Subject: `Unauthorized account access`
- Description: `I think someone took over my account and accessed it without permission.`

Explain:

> "This ticket may have an acceptable model confidence, but the business policy
> detects security-related language and requires human review."

## 4. Complete human review

Open **Tickets -> Ticket Queue**.

Select the review-required ticket. Change a field if appropriate, then click
**Complete human review**.

Explain:

> "Reviewed is not an automatic prediction. It appears only after a person
> completes the review and saves the final category, priority, and queue."

## 5. Batch processing

Use the sample file at `examples/batch_tickets.csv` or create a file with this format:

```csv
subject,description
Payment failed,My payment was declined and I need help.
Account access,My login is locked after too many attempts.
Security concern,I saw an unauthorized sign-in on my account.
```

Open **Tickets -> Batch Analysis**, upload the file, analyze it, and download
the results.

## 6. Intelligence

Open **Intelligence -> Analytics** to show live operational distributions.
Open **Intelligence -> Models** to show the actual held-out evaluation
metrics and confusion matrices.

## 7. Configuration

Open **Configuration -> Business Rules** to show that policy rules are
structured, visible, and separate from the trained models.

## Closing sentence

> "Relay combines supervised text classification with an auditable business
> policy layer and a human-in-the-loop exception workflow."

## What to point out

- The model only uses the ticket subject and description.
- Rules are applied after the model prediction.
- `Reviewed` appears only after a person completes the review.
- Metrics on Model Performance come from a held-out test set.
