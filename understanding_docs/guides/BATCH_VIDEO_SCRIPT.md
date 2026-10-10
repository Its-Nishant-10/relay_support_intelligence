# Batch Analysis Demo Script

## Video goal

Show how Relay analyzes several support tickets from one CSV file and applies the model and business policy to each row.

Suggested length: 60-90 seconds.

## Before recording

- Start the app with `streamlit run app.py`.
- Keep `examples/batch_tickets.csv` ready to upload.
- Open the Streamlit dashboard at `http://localhost:8501`.

## Screen sequence and narration

### 1. Open Batch Analysis

Navigate to **Tickets -> Batch Analysis**.

Say:

> "Instead of entering tickets one at a time, I can submit a CSV containing multiple incoming tickets. Relay expects two columns: `subject` and `description`."

### 2. Upload the sample file

Upload `examples/batch_tickets.csv` from the project root.

Say:

> "This sample contains payment, account access, security, VPN, and feature-question tickets. The subject and description are the only fields sent to the saved models."

### 3. Analyze the CSV

Click **Analyze CSV** and wait for the results table.

Say:

> "Relay now predicts a category, priority, queue, sentiment, and confidence for every row. The models run in inference mode; the application does not retrain when a file is uploaded."

### 4. Explain policy behavior

Point to the payment and security rows.

Say:

> "The machine-learning prediction is followed by the business policy layer. A refund-related ticket can receive a priority override, while security language can require human review even when model confidence is acceptable."

### 5. Download results

Click **Download predictions**.

Say:

> "The completed CSV can be downloaded for downstream work. It keeps the original ticket fields and adds the prediction and routing fields, including the final policy decision."

### 6. Close

Say:

> "Batch Analysis gives the support team a fast first pass while preserving confidence signals and human review for higher-risk tickets."

## Expected takeaways

- Required input columns are `subject` and `description`.
- The saved models classify each ticket without retraining.
- Policy rules can change the final priority or queue and can require review.
- The analyzed results are downloadable as a CSV.
