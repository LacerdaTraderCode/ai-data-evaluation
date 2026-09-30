"""Tests for turning rubric scores into pairwise preference data."""

from evaluation.golden_set import GOLDEN_SET, ScoredExample
from evaluation.preference_data import build_preference_pairs, total_score


def test_total_score_sums_every_criterion():
    example = ScoredExample(
        example_id="x",
        source_text="s",
        requested_format="f",
        candidate_summary="c",
        human_scores={"a": 2, "b": 1, "c": 0},
        justifications={"a": "", "b": "", "c": ""},
    )

    assert total_score(example) == 3


def test_pairs_only_form_between_examples_sharing_a_source_and_format():
    pairs = build_preference_pairs(GOLDEN_SET)

    for pair in pairs:
        assert pair.prompt.startswith("Summarize in")


def test_the_chosen_response_always_scores_higher_than_the_rejected_one():
    examples_by_id = {example.example_id: example for example in GOLDEN_SET}

    for pair in build_preference_pairs(GOLDEN_SET):
        chosen_example = next(
            e for e in examples_by_id.values() if e.candidate_summary == pair.chosen
        )
        rejected_example = next(
            e for e in examples_by_id.values() if e.candidate_summary == pair.rejected
        )
        assert total_score(chosen_example) > total_score(rejected_example)


def test_a_tie_produces_no_preference_pair():
    tied_a = ScoredExample(
        example_id="tied-a",
        source_text="same source",
        requested_format="one sentence",
        candidate_summary="summary a",
        human_scores={"accuracy": 1, "coverage": 1},
        justifications={"accuracy": "", "coverage": ""},
    )
    tied_b = ScoredExample(
        example_id="tied-b",
        source_text="same source",
        requested_format="one sentence",
        candidate_summary="summary b",
        human_scores={"accuracy": 2, "coverage": 0},
        justifications={"accuracy": "", "coverage": ""},
    )

    pairs = build_preference_pairs((tied_a, tied_b))

    assert pairs == []


def test_the_winning_criterion_is_the_one_with_the_largest_score_gap():
    # billing-good (8) ranks just above billing-incomplete (5); the score gap
    # is entirely on coverage, since billing-incomplete drops the timeline
    # and the performance result while matching everywhere else.
    pairs = build_preference_pairs(GOLDEN_SET)

    billing_pair = next(p for p in pairs if p.rejected.startswith("The billing service now uses"))

    assert billing_pair.winning_criterion == "coverage"
    assert billing_pair.score_gap == 3
