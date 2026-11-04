"""Pure-Python hybrid retrieval for the demo.

No paid APIs and no external model downloads. Two signals are combined:

1. BM25-style keyword scoring (term frequency, document length, IDF).
2. TF-IDF cosine similarity (a second, vector-style view of the same text).

Reranking step (see rerank()): the top candidates from the combined score
are re-scored with small, explainable bonuses for query-term coverage,
for a query phrase appearing verbatim, and for a query term appearing in
the section heading. No bonus invents new content; it only re-orders
passages that already exist in the sample documents.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "what", "when", "where",
    "how", "do", "does", "can", "i", "we", "you", "for", "of", "to", "in",
    "on", "and", "or", "if", "with", "without", "by", "at", "from", "it",
    "its", "this", "that", "my", "our", "please", "tell", "me", "about",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def content_terms(text: str) -> list[str]:
    return [t for t in tokenize(text) if t not in STOPWORDS]


@dataclass
class Chunk:
    doc: str
    section: str
    text: str
    tokens: list[str]

    @property
    def term_counts(self) -> Counter:
        return Counter(self.tokens)


def load_chunks(data_dir: Path) -> list[Chunk]:
    """Split each Markdown file into one chunk per '##' section."""
    chunks: list[Chunk] = []
    for path in sorted(data_dir.glob("*.md")):
        doc_title = path.stem.replace("_", " ").title()
        section = "Introduction"
        buffer: list[str] = []
        first_heading = None
        seen_section = False

        def flush() -> None:
            if buffer:
                text = " ".join(buffer).strip()
                if text:
                    chunks.append(
                        Chunk(doc=doc_title, section=section,
                              text=text, tokens=tokenize(text))
                    )
                buffer.clear()

        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("# "):
                first_heading = line[2:].strip()
                continue
            if line.startswith("## "):
                flush()
                section = line[3:].strip()
                seen_section = True
                continue
            # Text before the first section (e.g. the SAMPLE disclaimer)
            # is not a retrievable passage.
            if line and seen_section:
                buffer.append(line)
        flush()
        if first_heading:
            for c in chunks:
                if c.doc == doc_title:
                    c.doc = first_heading
    return chunks


class Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.n = len(chunks)
        self.avgdl = sum(len(c.tokens) for c in chunks) / max(self.n, 1)
        df: Counter = Counter()
        for c in chunks:
            for term in set(c.tokens):
                df[term] += 1
        self.df = df
        # TF-IDF vectors, built once at startup.
        self.idf = {
            term: math.log((self.n + 1) / (count + 1)) + 1.0
            for term, count in df.items()
        }
        self.tfidf: list[dict[str, float]] = []
        for c in chunks:
            counts = Counter(c.tokens)
            vec = {
                t: (1 + math.log(n)) * self.idf.get(t, 1.0)
                for t, n in counts.items()
            }
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self.tfidf.append({t: v / norm for t, v in vec.items()})

    def _bm25(self, chunk: Chunk, query_terms: list[str]) -> float:
        k1, b = 1.5, 0.75
        counts = chunk.term_counts
        dl = len(chunk.tokens)
        score = 0.0
        for term in query_terms:
            if term not in counts:
                continue
            idf = math.log((self.n - self.df[term] + 0.5) / (self.df[term] + 0.5) + 1)
            tf = counts[term]
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / self.avgdl))
        return score

    def _cosine(self, idx: int, query_terms: list[str]) -> float:
        counts = Counter(query_terms)
        qvec = {
            t: (1 + math.log(n)) * self.idf.get(t, 1.0)
            for t, n in counts.items()
        }
        norm = math.sqrt(sum(v * v for v in qvec.values())) or 1.0
        qvec = {t: v / norm for t, v in qvec.items()}
        doc = self.tfidf[idx]
        return sum(qvec.get(t, 0.0) * doc.get(t, 0.0) for t in qvec)

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        query_terms = content_terms(question)
        if not query_terms:
            return []
        scored = []
        for idx, chunk in enumerate(self.chunks):
            scored.append((idx, self._bm25(chunk, query_terms),
                           self._cosine(idx, query_terms)))
        max_bm25 = max((s[1] for s in scored), default=0.0) or 1.0
        combined = []
        for idx, bm25, cosine in scored:
            combined.append({
                "chunk": self.chunks[idx],
                "bm25": round(bm25, 4),
                "cosine": round(cosine, 4),
                "combined": 0.6 * (bm25 / max_bm25) + 0.4 * cosine,
            })
        combined.sort(key=lambda r: r["combined"], reverse=True)
        return self.rerank(question, query_terms, combined[:top_k])

    def rerank(self, question: str, query_terms: list[str],
               candidates: list[dict]) -> list[dict]:
        """Re-order top candidates with coverage / phrase / heading bonuses."""
        query_lower = question.lower()
        phrases = [" ".join(query_terms[i:i + 2])
                   for i in range(len(query_terms) - 1)]
        out = []
        for cand in candidates:
            chunk = cand["chunk"]
            text_lower = chunk.text.lower()
            present = {t for t in query_terms if t in chunk.tokens}
            coverage = len(present) / max(len(set(query_terms)), 1)
            phrase_bonus = 0.10 if any(p in text_lower for p in phrases) else 0.0
            heading_bonus = 0.05 if any(
                t in tokenize(chunk.section) for t in query_terms) else 0.0
            reranked = cand["combined"] + 0.15 * coverage + phrase_bonus + heading_bonus
            out.append({**cand, "coverage": round(coverage, 3),
                        "rerank_score": round(reranked, 4)})
        out.sort(key=lambda r: r["rerank_score"], reverse=True)
        return out
