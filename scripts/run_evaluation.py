"""CLI: scores the golden set with the Claude judge, reports agreement, writes preference data.

Usage:
    ANTHROPIC_API_KEY=... python -m scripts.run_evaluation
"""

import asyncio
import dataclasses
import json
import os
import sys

from evaluation.agreement import evaluate_agreement
from evaluation.golden_set import GOLDEN_SET
from evaluation.llm_judge import ClaudeJudge
from evaluation.preference_data import build_preference_pairs
from evaluation.rubric import SUMMARIZATION_RUBRIC

OUTPUT_PATH = "preference_data.jsonl"


async def score_golden_set(judge: ClaudeJudge) -> dict[str, dict[str, int]]:
    scores = {}
    for example in GOLDEN_SET:
        scores[example.example_id] = await judge.score(
            example.source_text,
            example.requested_format,
            example.candidate_summary,
            SUMMARIZATION_RUBRIC,
        )
    return scores


def print_agreement_report(report) -> None:
    for criterion_agreement in report.per_criterion:
        print(
            f"{criterion_agreement.criterion_name}: "
            f"exact match {criterion_agreement.exact_match_rate:.0%}, "
            f"mean abs diff {criterion_agreement.mean_absolute_difference:.2f}"
        )
    if report.disagreements:
        print("\nDisagreements:")
        for disagreement in report.disagreements:
            print(f"  {disagreement}")


def write_preference_data(path: str) -> int:
    pairs = build_preference_pairs(GOLDEN_SET)
    with open(path, "w") as output_file:
        for pair in pairs:
            output_file.write(json.dumps(dataclasses.asdict(pair)) + "\n")
    return len(pairs)


async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY to run the judge against the golden set.", file=sys.stderr)
        raise SystemExit(1)

    judge = ClaudeJudge(api_key=api_key, model=os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5"))
    judge_scores = await score_golden_set(judge)
    report = evaluate_agreement(GOLDEN_SET, judge_scores)
    print_agreement_report(report)

    pair_count = write_preference_data(OUTPUT_PATH)
    print(f"\nWrote {pair_count} preference pairs to {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
