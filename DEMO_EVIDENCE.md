# Demo Evidence — Grounded Retail Operations Assistant

Date: 2026-11-04. Live server run in this workspace, before the
9 PM ET / 8 PM CT project submission deadline.
Command: `/tmp/groa-venv2/bin/python -m uvicorn app:app --port 8002`
No Meta key was set for this run. No live Meta Model API call was made.
All answers below are verbatim server responses, not recreated text.
The UI file served is `static/index.html` in this repo.

## Health

`GET /health` — HTTP 200:

```json
{"status":"ok","documents":12,"meta_configured":false,"meta_model":"muse-spark-1.3"}
```

## UI

`GET /` — HTTP 200, 2081 bytes, serving `static/index.html`
("Grounded Retail Operations Assistant", question input, Answer,
Citations, Raw response). No screenshot was fabricated; the HTML file
itself is the UI evidence, and the JSON below is what it displays.

## Question 1 — returns with a receipt

`POST /ask` — HTTP 200:

```json
{"question":"How long do customers have to return an item with a receipt?","answer":"Customers may return an item within 30 days of purchase with a receipt for a full refund to the original payment method. Items must be unused and in their original packaging. Without a receipt, a return is limited to store credit at the lowest selling price in the last 30 days. Photo identification is required for a return without a receipt over 50 dollars.","supported":true,"citations":[{"doc":"Returns Policy","section":"Standard Returns","excerpt":"Customers may return an item within 30 days of purchase with a receipt for a full refund to the original payment method.","bm25":6.1815,"cosine":0.3439,"rerank_score":0.8376},{"doc":"Returns Policy","section":"Returns Without a Receipt","excerpt":"Without a receipt, a return is limited to store credit at the lowest selling price in the last 30 days.","bm25":3.9107,"cosine":0.2481,"rerank_score":0.5788}],"generation_mode":"extractive_no_model","retrieval_note":"No MODEL_API_KEY (or META_MODEL_API_KEY fallback) is set, so no Meta model was used. This is an extractive answer built only from the cited sample-document sentences. Retrieved 2 passage(s); top rerank score 0.8376."}
```

## Question 2 — high velocity counts

`POST /ask` — HTTP 200:

```json
{"question":"How often are high velocity items counted?","answer":"Count high velocity items every week. Count medium velocity items every two weeks. High velocity items carry 7 days of safety stock. Low velocity items carry 14 days of safety stock.","supported":true,"citations":[{"doc":"Inventory Policy","section":"Cycle Counts","excerpt":"Count high velocity items every week.","bm25":5.6069,"cosine":0.3951,"rerank_score":0.9481},{"doc":"Inventory Policy","section":"Reorder Thresholds","excerpt":"High velocity items carry 7 days of safety stock.","bm25":4.3906,"cosine":0.2713,"rerank_score":0.7684}],"generation_mode":"extractive_no_model","retrieval_note":"No MODEL_API_KEY (or META_MODEL_API_KEY fallback) is set, so no Meta model was used. This is an extractive answer built only from the cited sample-document sentences. Retrieved 2 passage(s); top rerank score 0.9481."}
```

## Question 3 — price changes

`POST /ask` — HTTP 200:

```json
{"question":"When do price changes take effect?","answer":"Price changes take effect on Monday mornings.","supported":true,"citations":[{"doc":"Merchandising Guide","section":"Price Changes","excerpt":"Price changes take effect on Monday mornings.","bm25":7.7992,"cosine":0.3789,"rerank_score":1.0516}],"generation_mode":"extractive_no_model","retrieval_note":"No MODEL_API_KEY (or META_MODEL_API_KEY fallback) is set, so no Meta model was used. This is an extractive answer built only from the cited sample-document sentences. Retrieved 1 passage(s); top rerank score 1.0516."}
```

## Question 4 — unsupported question, refused

`POST /ask` — HTTP 200:

```json
{"question":"What is the warranty on a toaster?","answer":"I don't have support in the provided documents for this question.","supported":false,"citations":[],"generation_mode":"refused_no_support","retrieval_note":"No passage scored above the support threshold, so the question was refused rather than answered from outside the sample documents."}
```

## Evaluation

`python evaluate.py` in the same venv: **4/4 checks passed**
(citation verbatimness and refusal on the 4 questions above; sample
documents only, not a benchmark).

## What this evidence does NOT show

- No live Meta Model API call: `meta_configured: false`,
  `generation_mode: extractive_no_model` throughout.
- No real retailer documents: `data/` contains 3 sample documents,
  12 passages, written for this demo.
- No GitHub push, video hosting, or hackathon submission is shown here.
