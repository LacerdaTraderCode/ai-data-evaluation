"""The curated golden set: source texts, candidate summaries, and human-assigned rubric scores.

Every score below was assigned by hand against the criteria in `rubric.py`,
which is why this file exists at all: an LLM judge is only useful once it can
be checked against labels a person actually stands behind.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoredExample:
    example_id: str
    source_text: str
    requested_format: str
    candidate_summary: str
    human_scores: dict[str, int]
    justifications: dict[str, str]


SOURCE_A = (
    "The team migrated the billing service from a monolith to three separate "
    "microservices last quarter: invoicing, payments, and refunds. Invoicing "
    "handles PDF generation and email delivery. Payments integrates with the "
    "card processor and retries failed charges up to three times. Refunds "
    "runs on a separate deployment schedule because it requires manual "
    "approval for amounts over $500. The migration took six weeks and cut "
    "average invoice generation time from 4.2 seconds to 0.9 seconds."
)

SOURCE_B = (
    "Database indexes speed up reads by letting the engine jump to matching "
    "rows instead of scanning the whole table, but every index adds write "
    "overhead because it must stay in sync with the data. A composite index "
    "on (user_id, created_at) only helps a query that filters on both "
    "columns in that order; it does little for a query that filters on "
    "created_at alone. Indexing every column is rarely a good default."
)

GOLDEN_SET: tuple[ScoredExample, ...] = (
    ScoredExample(
        example_id="billing-good",
        source_text=SOURCE_A,
        requested_format="two sentences",
        candidate_summary=(
            "The billing service was split into three microservices — invoicing, "
            "payments, and refunds — over a six-week migration. The change cut "
            "average invoice generation time from 4.2 to 0.9 seconds."
        ),
        human_scores={
            "factual_accuracy": 2,
            "coverage": 2,
            "conciseness": 2,
            "format_adherence": 2,
        },
        justifications={
            "factual_accuracy": (
                "Both numbers and the three service names match the source exactly."
            ),
            "coverage": "Covers the split, the timeline, and the performance result.",
            "conciseness": "No sentence repeats information already stated.",
            "format_adherence": "Exactly two sentences, as requested.",
        },
    ),
    ScoredExample(
        example_id="billing-hallucinated",
        source_text=SOURCE_A,
        requested_format="two sentences",
        candidate_summary=(
            "The billing service was rewritten in Go and split into three "
            "microservices, cutting invoice generation time by more than 80%. "
            "The migration was completed ahead of schedule."
        ),
        human_scores={
            "factual_accuracy": 0,
            "coverage": 1,
            "conciseness": 1,
            "format_adherence": 2,
        },
        justifications={
            "factual_accuracy": (
                "The source never mentions Go, and nothing says the migration finished early."
            ),
            "coverage": (
                "Mentions the split and the speed-up but drops the six-week timeline entirely."
            ),
            "conciseness": (
                "The 'ahead of schedule' claim adds nothing true, which reads as filler "
                "once it is wrong."
            ),
            "format_adherence": "Exactly two sentences, as requested.",
        },
    ),
    ScoredExample(
        example_id="billing-incomplete",
        source_text=SOURCE_A,
        requested_format="two sentences",
        candidate_summary=(
            "The billing service now uses microservices for invoicing, payments, and refunds."
        ),
        human_scores={
            "factual_accuracy": 2,
            "coverage": 0,
            "conciseness": 2,
            "format_adherence": 1,
        },
        justifications={
            "factual_accuracy": "What it states is accurate.",
            "coverage": "Drops the timeline and the performance result entirely, both main points.",
            "conciseness": "The single sentence has no filler.",
            "format_adherence": "One sentence where two were requested.",
        },
    ),
    ScoredExample(
        example_id="indexing-good",
        source_text=SOURCE_B,
        requested_format="one sentence",
        candidate_summary=(
            "Indexes speed up reads by letting the database jump to matching rows "
            "instead of scanning the table, at the cost of write overhead, and a "
            "composite index only helps queries that filter on its columns in order."
        ),
        human_scores={
            "factual_accuracy": 2,
            "coverage": 2,
            "conciseness": 2,
            "format_adherence": 2,
        },
        justifications={
            "factual_accuracy": (
                "Matches the source's claims about reads, writes, and composite index ordering."
            ),
            "coverage": "Covers the read speed-up, the write cost, and the composite index caveat.",
            "conciseness": "Dense but every clause adds a distinct point from the source.",
            "format_adherence": "One sentence, as requested.",
        },
    ),
    ScoredExample(
        example_id="indexing-wrong-format",
        source_text=SOURCE_B,
        requested_format="one sentence",
        candidate_summary=(
            "Indexes speed up reads. They add write overhead. Composite indexes "
            "need the right column order to help."
        ),
        human_scores={
            "factual_accuracy": 2,
            "coverage": 2,
            "conciseness": 1,
            "format_adherence": 0,
        },
        justifications={
            "factual_accuracy": "Every claim matches the source.",
            "coverage": "All three main points are present.",
            "conciseness": (
                "Splitting into three short sentences repeats 'indexes' where one "
                "sentence would not need to."
            ),
            "format_adherence": "Three sentences where one was requested.",
        },
    ),
    ScoredExample(
        example_id="indexing-embellished",
        source_text=SOURCE_B,
        requested_format="one sentence",
        candidate_summary=(
            "Database indexes, one of the most important tools in modern software "
            "engineering, dramatically speed up reads at some cost to writes."
        ),
        human_scores={
            "factual_accuracy": 1,
            "coverage": 0,
            "conciseness": 1,
            "format_adherence": 2,
        },
        justifications={
            "factual_accuracy": (
                "The superlative claim about importance is not in the source, though "
                "nothing contradicts it."
            ),
            "coverage": (
                "Drops the composite index point entirely, one of the source's three claims."
            ),
            "conciseness": "The opening clause is editorializing rather than informative.",
            "format_adherence": "One sentence, as requested.",
        },
    ),
)
