"""Tests for comparing judge scores against the human-labeled golden set."""

from evaluation.agreement import evaluate_agreement
from evaluation.golden_set import ScoredExample

EXAMPLE_A = ScoredExample(
    example_id="a",
    source_text="source",
    requested_format="one sentence",
    candidate_summary="candidate a",
    human_scores={"accuracy": 2, "coverage": 1},
    justifications={"accuracy": "matches", "coverage": "mostly complete"},
)

EXAMPLE_B = ScoredExample(
    example_id="b",
    source_text="source",
    requested_format="one sentence",
    candidate_summary="candidate b",
    human_scores={"accuracy": 0, "coverage": 2},
    justifications={"accuracy": "contradicts the source", "coverage": "complete"},
)


def test_perfect_agreement_has_a_100_percent_exact_match_rate_and_no_disagreements():
    judge_scores = {
        "a": {"accuracy": 2, "coverage": 1},
        "b": {"accuracy": 0, "coverage": 2},
    }

    report = evaluate_agreement((EXAMPLE_A, EXAMPLE_B), judge_scores)

    assert all(criterion.exact_match_rate == 1.0 for criterion in report.per_criterion)
    assert report.disagreements == ()


def test_a_disagreement_is_reported_with_both_scores():
    judge_scores = {
        "a": {"accuracy": 1, "coverage": 1},
        "b": {"accuracy": 0, "coverage": 2},
    }

    report = evaluate_agreement((EXAMPLE_A, EXAMPLE_B), judge_scores)

    assert "a/accuracy: human=2, judge=1" in report.disagreements


def test_mean_absolute_difference_reflects_the_size_of_the_disagreement():
    judge_scores = {
        "a": {"accuracy": 0, "coverage": 1},
        "b": {"accuracy": 0, "coverage": 2},
    }

    report = evaluate_agreement((EXAMPLE_A, EXAMPLE_B), judge_scores)

    accuracy_agreement = next(c for c in report.per_criterion if c.criterion_name == "accuracy")
    assert accuracy_agreement.mean_absolute_difference == 1.0
