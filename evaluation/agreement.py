"""Checks how well the LLM judge's scores agree with the human-labeled golden set."""

from dataclasses import dataclass

from evaluation.golden_set import ScoredExample


@dataclass(frozen=True)
class CriterionAgreement:
    criterion_name: str
    exact_match_rate: float
    mean_absolute_difference: float


@dataclass(frozen=True)
class AgreementReport:
    per_criterion: tuple[CriterionAgreement, ...]
    disagreements: tuple[str, ...]


def evaluate_agreement(
    examples: tuple[ScoredExample, ...], judge_scores: dict[str, dict[str, int]]
) -> AgreementReport:
    """Compare `judge_scores` (example_id -> {criterion: score}) against the human labels."""
    criterion_names = sorted({name for example in examples for name in example.human_scores})
    per_criterion: list[CriterionAgreement] = []
    disagreements: list[str] = []

    for criterion_name in criterion_names:
        differences = []
        for example in examples:
            human_score = example.human_scores[criterion_name]
            judge_score = judge_scores[example.example_id][criterion_name]
            differences.append(abs(human_score - judge_score))
            if human_score != judge_score:
                disagreements.append(
                    f"{example.example_id}/{criterion_name}: "
                    f"human={human_score}, judge={judge_score}"
                )

        exact_matches = sum(1 for difference in differences if difference == 0)
        per_criterion.append(
            CriterionAgreement(
                criterion_name=criterion_name,
                exact_match_rate=exact_matches / len(differences),
                mean_absolute_difference=sum(differences) / len(differences),
            )
        )

    return AgreementReport(per_criterion=tuple(per_criterion), disagreements=tuple(disagreements))
