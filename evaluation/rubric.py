"""Defines the summarization rubric: named criteria, each with an anchored 0-2 scale."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreLevel:
    value: int
    description: str


@dataclass(frozen=True)
class Criterion:
    name: str
    question: str
    levels: tuple[ScoreLevel, ...]

    def describe_level(self, value: int) -> str:
        for level in self.levels:
            if level.value == value:
                return level.description
        raise ValueError(f"{value} is not a valid score for {self.name!r}")


FACTUAL_ACCURACY = Criterion(
    name="factual_accuracy",
    question="Does every claim in the summary hold up against the source?",
    levels=(
        ScoreLevel(0, "Contains a claim that contradicts or is unsupported by the source."),
        ScoreLevel(1, "No contradictions, but includes an embellishment the source does not state."),
        ScoreLevel(2, "Every claim is directly supported by the source."),
    ),
)

COVERAGE = Criterion(
    name="coverage",
    question="Does the summary cover the source's main points?",
    levels=(
        ScoreLevel(0, "Misses a main point of the source."),
        ScoreLevel(1, "Covers every main point but omits a secondary one."),
        ScoreLevel(2, "Covers every main and secondary point."),
    ),
)

CONCISENESS = Criterion(
    name="conciseness",
    question="Does every sentence in the summary add information?",
    levels=(
        ScoreLevel(0, "Includes redundant or filler content."),
        ScoreLevel(1, "Mostly tight, with one redundant sentence or phrase."),
        ScoreLevel(2, "Every sentence adds information; nothing is redundant."),
    ),
)

FORMAT_ADHERENCE = Criterion(
    name="format_adherence",
    question="Does the summary follow the requested length and structure?",
    levels=(
        ScoreLevel(0, "Ignores the requested length or structure."),
        ScoreLevel(1, "Mostly follows the request, with a minor deviation."),
        ScoreLevel(2, "Fully follows the requested length and structure."),
    ),
)

SUMMARIZATION_RUBRIC: tuple[Criterion, ...] = (
    FACTUAL_ACCURACY,
    COVERAGE,
    CONCISENESS,
    FORMAT_ADHERENCE,
)
