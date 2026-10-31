"""Deterministic, offline RAG evaluation metrics.

These are regression signals, not substitutes for human or LLM-judge review.
"""

from collections.abc import Iterable, Mapping


def evaluate_case(
    *,
    retrieved_chunks: Iterable[Mapping],
    answer: str,
    expected_keywords: Iterable[str],
    expected_source: str | None = None,
) -> dict:
    chunks = list(retrieved_chunks)

    answer_text = (answer or "").casefold()

    retrieved_text = " ".join(
        str(chunk.get("text", ""))
        for chunk in chunks
    ).casefold()

    keywords = [
        word.casefold()
        for word in expected_keywords
    ]

    answer_hits = sum(
        keyword in answer_text
        for keyword in keywords
    )

    retrieval_hits = sum(
        keyword in retrieved_text
        for keyword in keywords
    )

    source_hit = (
        expected_source is None
        or any(
            chunk.get("source") == expected_source
            for chunk in chunks
        )
    )

    return {
        "retrieval_keyword_recall": (
            retrieval_hits / len(keywords)
            if keywords
            else 1.0
        ),
        "answer_keyword_coverage": (
            answer_hits / len(keywords)
            if keywords
            else 1.0
        ),
        "expected_source_retrieved": bool(source_hit),
        "retrieved_chunk_count": len(chunks),
        "passed": (
            bool(answer.strip())
            and source_hit
            and answer_hits == len(keywords)
        ),
    }