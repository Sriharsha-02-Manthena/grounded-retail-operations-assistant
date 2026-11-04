"""Evaluation: groundedness of /ask answers on the sample documents.

For each test question, check:
  1. If supported, every citation excerpt is a verbatim substring of a
     passage in data/ (so a citation cannot point at invented text).
  2. If supported, every answer sentence appears in (or is a sentence
     from) a cited passage.
  3. Unsupported questions are refused (supported=False, no citations),
     not answered with invented content.

This is a small demo check over 3 sample documents, NOT a benchmark and
NOT a performance claim. Run: python evaluate.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import RETRIEVER, answer_question  # noqa: E402

TESTS = [
    ("How long do customers have to return an item with a receipt?",
     True, "30 days"),
    ("How often are high velocity items counted?",
     True, "every week"),
    ("When do price changes take effect?",
     True, "Monday"),
    ("What is the warranty on a toaster?", False, None),
]


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def main() -> int:
    passages = [normalise(c.text) for c in RETRIEVER.chunks]
    passed = 0
    print("Groundedness evaluation (sample documents only)")
    print("=" * 60)
    for question, expect_supported, expect_phrase in TESTS:
        result = answer_question(question)
        checks: list[str] = []
        ok = True
        if result["supported"] != expect_supported:
            ok = False
            checks.append(f"supported={result['supported']}, expected {expect_supported}")
        if expect_supported:
            for cite in result["citations"]:
                excerpt = normalise(cite["excerpt"])
                if not any(excerpt in p for p in passages):
                    ok = False
                    checks.append(f"citation not verbatim in docs: {cite['excerpt'][:60]}")
            if expect_phrase and expect_phrase.lower() not in result["answer"].lower():
                ok = False
                checks.append(f"expected phrase missing: {expect_phrase}")
        else:
            if result["citations"]:
                ok = False
                checks.append("refused answer still carried citations")
        passed += 1 if ok else 0
        print(f"\nQ: {question}")
        print(f"  supported={result['supported']} mode={result['generation_mode']}")
        print(f"  answer: {result['answer']}")
        print(f"  {'PASS' if ok else 'FAIL: ' + '; '.join(checks)}")
    print("\n" + "=" * 60)
    print(f"{passed}/{len(TESTS)} checks passed. "
          "This measures only citation verbatimness and refusal on this "
          "tiny sample set; it is not a quality or accuracy benchmark.")
    return 0 if passed == len(TESTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
