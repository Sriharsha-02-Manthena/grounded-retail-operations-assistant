"""Grounded Retail Operations Assistant - FastAPI demo.

Answer policy (this is the whole honesty mechanism):
  - Answers are built ONLY from sentences in retrieved sample documents.
  - Every answer sentence comes from a cited passage, and every citation
    excerpt is a verbatim substring of its passage.
  - If no passage overlaps the question, the app refuses instead of
    inventing an answer: supported=False, no citations.
  - Without a MODEL_API_KEY (fallback: META_MODEL_API_KEY),
    generation_mode is "extractive_no_model" and the response says no
    Meta model was used.
  - With a key, Meta Muse Spark may draft a summary of the same passages,
    but the extractive cited answer is still returned alongside it as
    `meta_draft` (clearly labelled, untested without a live key), and the
    cited answer remains the answer of record.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import meta_client
from retrieval import Retriever, content_terms, load_chunks

BASE_DIR = Path(__file__).resolve().parent
RETRIEVER = Retriever(load_chunks(BASE_DIR / "data"))

# Below this combined rerank score, retrieval is treated as no support.
MIN_SCORE = 0.10

app = FastAPI(title="Grounded Retail Operations Assistant (demo)")


class AskRequest(BaseModel):
    question: str


def _pick_sentences(text: str, query_terms: list[str], limit: int = 2) -> list[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    ranked = sorted(
        sentences,
        key=lambda s: sum(1 for t in query_terms if t in s.lower()),
        reverse=True,
    )
    picked = [s for s in ranked if any(t in s.lower() for t in query_terms)][:limit]
    return picked or sentences[:1]


def answer_question(question: str) -> dict:
    question = (question or "").strip()
    if not question:
        return {
            "question": question, "answer": "", "supported": False,
            "citations": [], "generation_mode": "none",
            "retrieval_note": "Empty question; no retrieval was run.",
        }
    results = RETRIEVER.search(question, top_k=5)
    if not results or results[0]["rerank_score"] < MIN_SCORE:
        return {
            "question": question,
            "answer": "I don't have support in the provided documents for this question.",
            "supported": False, "citations": [],
            "generation_mode": "refused_no_support",
            "retrieval_note": (
                "No passage scored above the support threshold, so the "
                "question was refused rather than answered from outside "
                "the sample documents."
            ),
        }

    # Keep the top passage, plus a second one only if it is comparably
    # strong (at least half the top rerank score). This stops a weak
    # second passage adding off-topic sentences to an otherwise good answer.
    top_score = results[0]["rerank_score"]
    top = [r for r in results[:2] if r["rerank_score"] >= 0.5 * top_score]
    query_terms = content_terms(question)
    answer_parts: list[str] = []
    citations: list[dict] = []
    passages: list[dict] = []
    for result in top:
        chunk = result["chunk"]
        sentences = _pick_sentences(chunk.text, query_terms)
        answer_parts.extend(sentences)
        excerpt = sentences[0]
        citations.append({
            "doc": chunk.doc, "section": chunk.section, "excerpt": excerpt,
            "bm25": result["bm25"], "cosine": result["cosine"],
            "rerank_score": result["rerank_score"],
        })
        passages.append({"doc": chunk.doc, "section": chunk.section,
                         "text": chunk.text})

    if meta_client.is_configured():
        meta_text, meta_error = meta_client.generate_answer(question, passages)
        if meta_text:
            mode = "meta_muse_spark_draft_plus_extractive_citations"
            note = (
                f"Meta model {meta_client.MODEL_NAME} drafted a summary of "
                "the cited passages; the extractive answer below, built "
                "only from cited sentences, is the answer of record."
            )
        else:
            meta_text, mode = None, "extractive_fallback_after_meta_error"
            note = (f"Meta call did not return text ({meta_error}); "
                    "falling back to extractive cited answer.")
    else:
        meta_text, mode = None, "extractive_no_model"
        note = (
            "No MODEL_API_KEY (or META_MODEL_API_KEY fallback) is set, "
            "so no Meta model was used. "
            "This is an extractive answer built only from the cited "
            "sample-document sentences."
        )

    response = {
        "question": question,
        "answer": " ".join(answer_parts),
        "supported": True,
        "citations": citations,
        "generation_mode": mode,
        "retrieval_note": (
            f"{note} Retrieved {len(top)} passage(s); "
            f"top rerank score {top[0]['rerank_score']}."
        ),
    }
    if meta_text:
        response["meta_draft"] = meta_text
    return response


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/ask")
def ask(req: AskRequest):
    return answer_question(req.question)


@app.get("/health")
def health():
    return {"status": "ok", "documents": len(RETRIEVER.chunks),
            "meta_configured": meta_client.is_configured(),
            "meta_model": meta_client.MODEL_NAME}
