"""Applies the rubric to a candidate summary using Claude as the judge."""

import json
import re

import httpx2

from evaluation.rubric import Criterion

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


def build_judge_prompt(
    source_text: str,
    requested_format: str,
    candidate_summary: str,
    criteria: tuple[Criterion, ...],
) -> str:
    criteria_block = "\n\n".join(
        f"{criterion.name} — {criterion.question}\n"
        + "\n".join(f"  {level.value}: {level.description}" for level in criterion.levels)
        for criterion in criteria
    )
    return (
        "Score the candidate summary against each criterion below. "
        "Respond with only a JSON object mapping each criterion name to its integer score, "
        "nothing else.\n\n"
        f"Criteria:\n{criteria_block}\n\n"
        f"Requested format: {requested_format}\n"
        f"Source:\n{source_text}\n\n"
        f"Candidate summary:\n{candidate_summary}"
    )


def _parse_scores(raw_text: str, criteria: tuple[Criterion, ...]) -> dict[str, int]:
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match is None:
        raise ValueError(f"Judge response did not contain a JSON object: {raw_text!r}")
    scores = json.loads(match.group(0))
    expected_names = {criterion.name for criterion in criteria}
    if set(scores) != expected_names:
        raise ValueError(f"Judge scored {set(scores)}, expected {expected_names}")
    return {name: int(value) for name, value in scores.items()}


class ClaudeJudge:
    def __init__(self, api_key: str, model: str, client: httpx2.AsyncClient | None = None):
        self._api_key = api_key
        self._model = model
        self._client = client or httpx2.AsyncClient()

    async def score(
        self,
        source_text: str,
        requested_format: str,
        candidate_summary: str,
        criteria: tuple[Criterion, ...],
    ) -> dict[str, int]:
        prompt = build_judge_prompt(source_text, requested_format, candidate_summary, criteria)
        response = await self._client.post(
            CLAUDE_API_URL,
            headers={"x-api-key": self._api_key, "anthropic-version": ANTHROPIC_VERSION},
            json={
                "model": self._model,
                "max_tokens": 256,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        raw_text = response.json()["content"][0]["text"]
        return _parse_scores(raw_text, criteria)
