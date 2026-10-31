from evaluation.metrics import evaluate_case


def test_golden_case_passes_when_answer_and_source_match():
    result = evaluate_case(
        retrieved_chunks=[
            {
                "text": (
                    "Use the account recovery workflow "
                    "for account lockouts."
                ),
                "source": "it_support_sop.md",
            }
        ],
        answer="Use the account recovery workflow.",
        expected_keywords=["account", "recovery"],
        expected_source="it_support_sop.md",
    )

    assert result["passed"] is True
    assert result["retrieval_keyword_recall"] == 1.0
    assert result["answer_keyword_coverage"] == 1.0


def test_golden_case_fails_when_expected_source_is_missing():
    result = evaluate_case(
        retrieved_chunks=[
            {
                "text": "account recovery",
                "source": "other.md",
            }
        ],
        answer="account recovery",
        expected_keywords=["account", "recovery"],
        expected_source="it_support_sop.md",
    )

    assert result["passed"] is False
    assert result["expected_source_retrieved"] is False