# Grounded Retail Operations Assistant — Submission

## Team Name

RAVANA

## Track

Indie Dev Track

## Problem statement

Build for Your World

## Project Description

Grounded Retail Operations Assistant is a FastAPI web app that answers retail operations questions from internal documents with cited, source-backed answers. A user asks, for example, how long customers have to return an item with a receipt, how often high velocity items are counted, or when price changes take effect, and the app returns only sentences taken from retrieved sample documents, each with a document and section citation. Retrieval is hybrid: BM25-style keyword scoring plus TF-IDF cosine similarity in pure Python, followed by a reranking step using query-term coverage, a verbatim phrase bonus, and a section-heading bonus. If no passage supports a question, the app refuses instead of inventing an answer. An evaluation script checks that every citation excerpt is verbatim in the sample documents and that unsupported questions are refused; it passes 4 of 4 checks on the sample set. The demo uses 3 clearly labelled sample documents (inventory policy, merchandising guide, returns policy; 12 passages). It is a working demo, not a production system and not a real retailer's data.

## Public GitHub Repository

https://github.com/Sriharsha-02-Manthena/grounded-retail-operations-assistant

## 3-Min Demo Video

https://github.com/Sriharsha-02-Manthena/grounded-retail-operations-assistant/blob/main/demo-video.mp4

## How Meta products were used

The project implements a Meta Model API client in `meta_client.py` using the OpenAI-compatible API: base URL `https://api.meta.ai/v1`, model `muse-spark-1.3`. The client is called only when a key is set, checked as `MODEL_API_KEY` first (the official name), with `META_MODEL_API_KEY` as a fallback. When a key is set, the client sends the retrieved passages as context with an instruction to answer only from those passages, and its text is returned only as a labelled `meta_draft`; the extractive cited answer remains the answer of record. No live Meta call was run in this demo, because no key was available or invented, and that code path is untested. The answers shown in the demo and video are therefore extractive cited answers, and every response says so explicitly (`generation_mode: extractive_no_model`). No Meta-generated answer is claimed where none was produced.

## Why Meta AI is valuable to this solution

Retail operations questions are high stakes for the people who act on them: a wrong return window, count frequency, or price date costs time and trust. Meta's models are valuable here not as a source of new facts, but as a reasoning layer over retrieved, cited passages: they can turn the right passages into a clear, readable answer while the system keeps citations and a refusal path as the guardrail. That combination, a capable model constrained to source-backed passages, is what would make this useful in a real store or operations team, where an unsupported answer is worse than no answer. This demo shows the guardrail side working; the model side is implemented and ready to test with a real key, and is not overstated here.

## How likely are you to build with Meta Model API in the future?

Very likely

## How would you describe your overall opinion of Meta Model API?

Neutral
