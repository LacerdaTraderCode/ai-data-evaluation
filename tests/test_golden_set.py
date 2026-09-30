"""Sanity checks on the golden set itself: a labeled dataset is a deliverable too."""

from evaluation.golden_set import GOLDEN_SET
from evaluation.rubric import SUMMARIZATION_RUBRIC

_CRITERION_NAMES = {criterion.name for criterion in SUMMARIZATION_RUBRIC}
_VALID_SCORES = {level.value for criterion in SUMMARIZATION_RUBRIC for level in criterion.levels}


def test_every_example_has_a_unique_id():
    ids = [example.example_id for example in GOLDEN_SET]

    assert len(ids) == len(set(ids))


def test_every_example_is_scored_on_every_rubric_criterion():
    for example in GOLDEN_SET:
        assert set(example.human_scores) == _CRITERION_NAMES


def test_every_example_has_a_justification_for_every_score():
    for example in GOLDEN_SET:
        assert set(example.justifications) == _CRITERION_NAMES
        for justification in example.justifications.values():
            assert justification.strip() != ""


def test_every_score_is_within_the_rubrics_valid_range():
    for example in GOLDEN_SET:
        for score in example.human_scores.values():
            assert score in _VALID_SCORES


def test_the_golden_set_contains_more_than_one_quality_level_per_source():
    scores_by_source: dict[str, set[int]] = {}
    for example in GOLDEN_SET:
        total = sum(example.human_scores.values())
        scores_by_source.setdefault(example.source_text, set()).add(total)

    for totals in scores_by_source.values():
        assert len(totals) > 1
