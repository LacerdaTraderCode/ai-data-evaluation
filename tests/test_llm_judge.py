"""Tests for prompt construction, response parsing, and the Claude-backed judge."""

import json

import httpx2
import pytest

from evaluation.llm_judge import ClaudeJudge, build_judge_prompt
from evaluation.rubric import SUMMARIZATION_RUBRIC


def test_prompt_includes_every_criterion_and_all_of_its_score_levels():
    prompt = build_judge_prompt("source text", "one sentence", "candidate", SUMMARIZATION_RUBRIC)

    for criterion in SUMMARIZATION_RUBRIC:
        assert criterion.name in prompt
        for level in criterion.levels:
            assert level.description in prompt


def test_prompt_includes_the_source_format_and_candidate():
    prompt = build_judge_prompt(
        "the source text", "two sentences", "the candidate summary", SUMMARIZATION_RUBRIC
    )

    assert "the source text" in prompt
    assert "two sentences" in prompt
    assert "the candidate summary" in prompt


async def test_judge_parses_a_well_formed_score_response(build_mock_client):
    captured = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        captured["body"] = json.loads(request.content)
        return httpx2.Response(
            200,
            json={
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "factual_accuracy": 2,
                                "coverage": 1,
                                "conciseness": 2,
                                "format_adherence": 2,
                            }
                        ),
                    }
                ]
            },
        )

    judge = ClaudeJudge(api_key="test-key", model="test-model", client=build_mock_client(handler))

    scores = await judge.score("source", "one sentence", "candidate", SUMMARIZATION_RUBRIC)

    assert scores == {
        "factual_accuracy": 2,
        "coverage": 1,
        "conciseness": 2,
        "format_adherence": 2,
    }
    assert captured["body"]["model"] == "test-model"


async def test_judge_tolerates_surrounding_prose_around_the_json_object(build_mock_client):
    reply_text = (
        "Here is my assessment:\n"
        '{"factual_accuracy": 1, "coverage": 1, "conciseness": 1, "format_adherence": 1}\n'
        "Let me know if you need more detail."
    )

    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json={"content": [{"type": "text", "text": reply_text}]})

    judge = ClaudeJudge(api_key="test-key", model="test-model", client=build_mock_client(handler))

    scores = await judge.score("source", "one sentence", "candidate", SUMMARIZATION_RUBRIC)

    assert scores["coverage"] == 1


async def test_judge_raises_a_clear_error_when_a_criterion_is_missing(build_mock_client):
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            200, json={"content": [{"type": "text", "text": '{"factual_accuracy": 2}'}]}
        )

    judge = ClaudeJudge(api_key="test-key", model="test-model", client=build_mock_client(handler))

    with pytest.raises(ValueError, match="expected"):
        await judge.score("source", "one sentence", "candidate", SUMMARIZATION_RUBRIC)


async def test_judge_raises_a_clear_error_when_the_response_has_no_json(build_mock_client):
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            200, json={"content": [{"type": "text", "text": "I refuse to answer."}]}
        )

    judge = ClaudeJudge(api_key="test-key", model="test-model", client=build_mock_client(handler))

    with pytest.raises(ValueError, match="did not contain"):
        await judge.score("source", "one sentence", "candidate", SUMMARIZATION_RUBRIC)
