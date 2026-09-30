"""Tests for the parts of the CLI script that do not require a live API key."""

import json

from evaluation.golden_set import GOLDEN_SET
from scripts.run_evaluation import write_preference_data


def test_write_preference_data_produces_one_valid_json_object_per_line(tmp_path):
    output_path = tmp_path / "preference_data.jsonl"

    pair_count = write_preference_data(str(output_path))

    lines = output_path.read_text().splitlines()
    assert len(lines) == pair_count
    for line in lines:
        record = json.loads(line)
        assert set(record) == {"prompt", "chosen", "rejected", "winning_criterion", "score_gap"}


def test_write_preference_data_returns_a_count_consistent_with_the_golden_set_size(tmp_path):
    pair_count = write_preference_data(str(tmp_path / "out.jsonl"))

    assert 0 < pair_count < len(GOLDEN_SET)
