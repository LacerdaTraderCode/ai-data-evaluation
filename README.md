# AI Data & Evaluation — Rubric-Based Fine-Tuning Pipeline

A complete evaluation pipeline for LLM outputs: a hand-labeled golden set, an anchored multi-criteria rubric, an LLM judge that applies it automatically, an agreement check between the two, and a converter that turns the scores into preference data shaped for a fine-tuning job.

## The task

The pipeline evaluates a fixed task — summarizing a short source document to a requested length — so the rubric, the golden set, and the judge all stay comparable across examples. The task itself is a vehicle; the pipeline generalizes to any task an LLM's output can be judged against written criteria.

## The pipeline

1. **`evaluation/rubric.py`** — four criteria (factual accuracy, coverage, conciseness, format adherence), each scored 0–2 with a written description per level. No criterion is scored on an unanchored 1-to-5 scale.
2. **`evaluation/golden_set.py`** — six hand-scored examples: two source documents, three candidate summaries each, with a deliberate quality difference (a clean summary, one with a hallucinated claim, one missing a key point, and so on) so the pipeline's output is checkable against a known answer.
3. **`evaluation/llm_judge.py`** — asks Claude to score a candidate against the same rubric the human labels used.
4. **`evaluation/agreement.py`** — compares the judge's scores to the human labels per criterion: exact-match rate, mean absolute difference, and a list of every disagreement. A judge is not trustworthy at scale until this comparison has been run and reviewed.
5. **`evaluation/preference_data.py`** — ranks same-source, same-format examples by total score and emits adjacent pairs as `{prompt, chosen, rejected, winning_criterion, score_gap}` records, the shape used by DPO-style preference-tuning datasets.

Run the full pipeline end to end:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
python -m scripts.run_evaluation
```

This scores the golden set with the judge, prints the agreement report, and writes `preference_data.jsonl`.

## Why the golden set matters as much as the code

See [`docs/rubric_methodology.md`](docs/rubric_methodology.md) for why the rubric has four criteria instead of one overall score, why each is scored 0–2 with a written anchor instead of 1–5, and why an LLM judge should never be trusted without a golden-set agreement check first.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite covers the rubric's internal consistency, the golden set's own integrity (every example scored on every criterion, every score justified), prompt construction and response parsing for the judge (mocked, no API key needed), the agreement math, and preference-pair generation — including that a tie between two examples produces no pair.

## License

MIT — see [LICENSE](LICENSE).
