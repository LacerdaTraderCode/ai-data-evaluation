"""Turns rubric scores into pairwise preference records, ready for a fine-tuning job.

The shape mirrors the "chosen" / "rejected" convention used by common
preference-tuning formats (e.g. DPO datasets): each record pairs a stronger
and a weaker response to the same prompt and states which criterion decided it.
"""

from dataclasses import dataclass
from itertools import pairwise

from evaluation.golden_set import ScoredExample


@dataclass(frozen=True)
class PreferencePair:
    prompt: str
    chosen: str
    rejected: str
    winning_criterion: str
    score_gap: int


def total_score(example: ScoredExample) -> int:
    return sum(example.human_scores.values())


def build_preference_pairs(examples: tuple[ScoredExample, ...]) -> list[PreferencePair]:
    """Pair examples that share a source and requested format, ranked by total score.

    Only adjacent ranks within a group become a pair — comparing the best
    example against the worst, skipping the middle one, would tell a
    fine-tuning run less about *why* one response beats another than
    comparing each example to its closest competitor does. Pairs with a
    zero-point gap are dropped entirely: a tie carries no preference signal.
    """
    grouped: dict[tuple[str, str], list[ScoredExample]] = {}
    for example in examples:
        key = (example.source_text, example.requested_format)
        grouped.setdefault(key, []).append(example)

    pairs: list[PreferencePair] = []
    for group in grouped.values():
        ranked = sorted(group, key=total_score, reverse=True)
        for better, worse in pairwise(ranked):
            gap = total_score(better) - total_score(worse)
            if gap == 0:
                continue
            deciding_criterion = max(
                better.human_scores,
                key=lambda name: better.human_scores[name] - worse.human_scores[name],
            )
            prompt = f"Summarize in {better.requested_format}:\n\n{better.source_text}"
            pairs.append(
                PreferencePair(
                    prompt=prompt,
                    chosen=better.candidate_summary,
                    rejected=worse.candidate_summary,
                    winning_criterion=deciding_criterion,
                    score_gap=gap,
                )
            )

    return pairs
