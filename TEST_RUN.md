# Test Run

## Re-test after MODEL_API_KEY alignment — 2026-11-04

Meta env-var change made in this re-test: `meta_client.py` now checks
`MODEL_API_KEY` first (official Meta Model API name), with
`META_MODEL_API_KEY` as a fallback. `app.py`, `static/index.html`, and
`README.md` were updated to match. Base URL remains
`https://api.meta.ai/v1`, model remains `muse-spark-1.3`.

Environment: fresh venv `/tmp/groa-venv2`,
`/tmp/groa-venv2/bin/pip install -r requirements.txt`,
`/tmp/groa-venv2/bin/python evaluate.py`, then
`/tmp/groa-venv2/bin/python -m uvicorn app:app --port 8002`.
No real Meta key was set or invented for this run.

Evaluation: **4/4 checks passed** (same 4 questions as the first run:
returns with receipt, high velocity count frequency, price change
timing, and toaster-warranty refusal).

Live server:
- `GET /health` returned
  `{"status": "ok", "documents": 12, "meta_configured": false, "meta_model": "muse-spark-1.3"}`
- `GET /` returned HTTP 200, 2081 bytes.
- `POST /ask` (3 supported questions + 1 refusal) all returned HTTP
  200. Supported answers were in `generation_mode: extractive_no_model`,
  with a retrieval note now reading: "No MODEL_API_KEY (or
  META_MODEL_API_KEY fallback) is set, so no Meta model was used."
  Top rerank scores: returns 0.8376, cycle counts 0.9481, price changes
  1.0516. The toaster question was refused with `supported: false`
  and no citations.
- Env-var precedence check (test values only, no live call):
  fallback `META_MODEL_API_KEY` alone gives `is_configured()=True`;
  `MODEL_API_KEY` takes precedence over the fallback when both are set;
  neither set gives `is_configured()=False`.

Full live responses from this run are saved in `DEMO_EVIDENCE.md`.
No live Meta Model API call was tested, for the same reason as before:
no key was available or invented.

---

# Test Run (first run, earlier on 2026-11-04)

Date: 2026-11-04 (run in this workspace, before the 9 PM ET / 8 PM CT
project submission deadline).

Environment note: the system Python here is externally managed, so the
test used a temporary venv (`python3 -m venv /tmp/groa-venv`,
`/tmp/groa-venv/bin/pip install -r requirements.txt`). A reviewer's
normal `pip install -r requirements.txt` inside their own venv is the
intended path in README.md. No Meta key was set for this run.

## Commands

```bash
cd grounded-retail-ops-assistant
python evaluate.py
python -m uvicorn app:app --port 8001
curl http://127.0.0.1:8001/health
curl -X POST http://127.0.0.1:8001/ask -H 'Content-Type: application/json' \
  -d '{"question": "..."}'
curl http://127.0.0.1:8001/
```

## Evaluation output (4/4 passed)

```
Groundedness evaluation (sample documents only)
Q: How long do customers have to return an item with a receipt?
  supported=True mode=extractive_no_model
  answer: Customers may return an item within 30 days of purchase with a receipt for a full refund to the original payment method. Items must be unused and in their original packaging. Without a receipt, a return is limited to store credit at the lowest selling price in the last 30 days. Photo identification is required for a return without a receipt over 50 dollars.
  PASS
Q: How often are high velocity items counted?
  supported=True mode=extractive_no_model
  answer: Count high velocity items every week. Count medium velocity items every two weeks. High velocity items carry 7 days of safety stock. Low velocity items carry 14 days of safety stock.
  PASS
Q: When do price changes take effect?
  supported=True mode=extractive_no_model
  answer: Price changes take effect on Monday mornings.
  PASS
Q: What is the warranty on a toaster?
  supported=False mode=refused_no_support
  answer: I don't have support in the provided documents for this question.
  PASS
4/4 checks passed. This measures only citation verbatimness and refusal on this
tiny sample set; it is not a quality or accuracy benchmark.
```

## Live server output

Health:

```json
{"status": "ok", "documents": 12, "meta_configured": false, "meta_model": "muse-spark-1.3"}
```

UI: `GET /` returned status 200.

### Test question 1

Question: How long do customers have to return an item with a receipt?

Answer: Customers may return an item within 30 days of purchase with a
receipt for a full refund to the original payment method. Items must be
unused and in their original packaging. Without a receipt, a return is
limited to store credit at the lowest selling price in the last 30 days.
Photo identification is required for a return without a receipt over
50 dollars.

Citations: Returns Policy — Standard Returns; Returns Policy —
Returns Without a Receipt. Mode: `extractive_no_model`.

### Test question 2

Question: How often are high velocity items counted?

Answer: Count high velocity items every week. Count medium velocity
items every two weeks. High velocity items carry 7 days of safety stock.
Low velocity items carry 14 days of safety stock.

Citations: Inventory Policy — Cycle Counts; Inventory Policy —
Reorder Thresholds. Mode: `extractive_no_model`.

### Test question 3

Question: When do price changes take effect?

Answer: Price changes take effect on Monday mornings.

Citation: Merchandising Guide — Price Changes.
Mode: `extractive_no_model`.

## What was NOT tested

- No live Meta Model API call: no key was set or invented, so
  `meta_client.py` was exercised only through its no-key fallback path.
  A live call with a real key remains untested.
- No hackathon submission, GitHub push, or video recording was done.
