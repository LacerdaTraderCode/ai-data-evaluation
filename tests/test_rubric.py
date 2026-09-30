"""Tests for the rubric definitions."""

import pytest

from evaluation.rubric import SUMMARIZATION_RUBRIC, Criterion, ScoreLevel


def test_every_criterion_in_the_rubric_has_a_score_for_every_level_it_defines():
    for criterion in SUMMARIZATION_RUBRIC:
        for level in criterion.levels:
            assert criterion.describe_level(level.value) == level.description


def test_describe_level_rejects_a_score_outside_the_defined_scale():
    criterion = Criterion(
        name="example",
        question="?",
        levels=(ScoreLevel(0, "bad"), ScoreLevel(1, "good")),
    )

    with pytest.raises(ValueError, match="not a valid score"):
        criterion.describe_level(5)


def test_the_rubric_has_no_duplicate_criterion_names():
    names = [criterion.name for criterion in SUMMARIZATION_RUBRIC]

    assert len(names) == len(set(names))


def test_every_criterion_scale_starts_at_zero_and_has_no_gaps():
    for criterion in SUMMARIZATION_RUBRIC:
        values = sorted(level.value for level in criterion.levels)

        assert values == list(range(len(values)))
