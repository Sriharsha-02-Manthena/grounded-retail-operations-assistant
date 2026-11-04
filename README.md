# Grounded Retail Operations Assistant

By Sriharsha Manthena

Built for the Meta Global AI Developer Hackathon, Indie Dev Track,
**Build for Your World** theme. Project: a grounded document assistant
for retail operations teams that answers product, merchandising and
inventory questions from internal documents with cited, source-backed
answers.

## What is actually built

- A FastAPI app (`app.py`) with a `POST /ask` endpoint.
- Hybrid retrieval in pure Python (`retrieval.py`): BM25-style keyword
  scoring plus TF-IDF cosine similarity, followed by a small reranking
  step (query-term coverage, verbatim phrase bonus, section-heading
  bonus). No paid APIs, no external model downloads.
- A simple web UI at `/` (`static/index.html`): type a question, see
  the cited answer.
- An evaluation script (`evaluate.py`) that checks citation
  verbatimness and refusal for unsupported questions.
- Three sample documents in `data/` (inventory policy, merchandising
  guide, returns policy). They are clearly labelled sample content
  written for this demo. They are not a real retailer's documents.

## How to run

```bash
cd grounded-retail-ops-assistant
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Then open http://127.0.0.1:8000/ and try, for example:

1. How long do customers have to return an item with a receipt?
2. How often are high velocity items counted?
3. When do price changes take effect?

Or call the API directly:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "How long do customers have to return an item with a receipt?"}'
```

Run the evaluation:

```bash
python evaluate.py
```

## Meta Model API integration: what it does and does not do

- `meta_client.py` calls the Meta Model API (base URL
  `https://api.meta.ai/v1`, model `muse-spark-1.3` by default) using an
  OpenAI-compatible chat completion, with the retrieved passages as
  context and an instruction to answer only from those passages.
- It runs **only** if a key is set in the environment, checked in this
  order (official name first, per the Meta Model API docs):
  `MODEL_API_KEY`, then `META_MODEL_API_KEY` as a fallback:
  `MODEL_API_KEY=... uvicorn app:app --port 8000`.
  Optional overrides: `META_MODEL_API_BASE_URL`, `META_MODEL_NAME`.
- **Without a key, no Meta model is used.** The app still works with
  extractive cited answers, and every response says so
  (`generation_mode: extractive_no_model`). It never claims a Meta
  model generated an answer when it did not.
- A live Meta call has **not** been tested in this build (no key was
  available or invented for it). With a key, the Meta text is returned
  only as a labelled `meta_draft`; the extractive cited answer remains
  the answer of record, because a draft is not automatically grounded.
- If a Meta call fails, the app falls back to the extractive answer
  and says so in `retrieval_note`.

## Honesty and limits

- Answers are built only from sentences in the sample documents. If no
  passage supports a question, the app refuses instead of inventing an
  answer (see the toaster-warranty case in `evaluate.py`).
- The sample set is tiny (3 documents). Real use would need the user's
  real documents, a larger corpus, and proper access control; none of
  that is claimed here.
- No performance numbers are claimed. `evaluate.py` reports only
  citation verbatimness and refusal on 4 hand-written test questions;
  it is not a benchmark.
- Repository: https://github.com/Sriharsha-02-Manthena/grounded-retail-operations-assistant

## Demo steps for a reviewer

1. Start the app with the commands above.
2. Ask the three sample questions and check that each answer sentence
   matches a cited passage shown below it.
3. Ask an unsupported question (for example, about a toaster warranty)
   and check that it is refused.
4. Run `python evaluate.py` and read its pass/fail output.
5. Optionally, set `MODEL_API_KEY` (fallback: `META_MODEL_API_KEY`)
   and repeat step 2 to see the labelled Meta draft alongside the
   extractive answer.
