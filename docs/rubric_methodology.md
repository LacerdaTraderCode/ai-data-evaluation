# Rubric Methodology

The code in this repository is the easy part. What actually determines whether an evaluation pipeline is trustworthy is the rubric it scores against and the labeled data it is checked on — this document is about those two things.

## Why four criteria instead of one overall score

A single 1-to-5 "quality" score collapses several different failure modes into one number. A summary that hallucinates a fact and a summary that is merely a bit wordy are both "not perfect," but they are not the same problem, and a fine-tuning run learns nothing about *which* problem to fix from a single scalar. Splitting the rubric into `factual_accuracy`, `coverage`, `conciseness`, and `format_adherence` means every score change has a specific, nameable cause, and `build_preference_pairs` can report a `winning_criterion` for every pair instead of an unexplained "A is better."

The four criteria were chosen to be independent of each other: a summary can be fully accurate and still incomplete, or complete and still redundant. Criteria that tend to move together are redundant with each other and add labeling cost without adding signal.

## Why 0–2 instead of 1–5

A wider scale invites false precision. The practical difference between a 3 and a 4 on a 1-to-5 scale is rarely something two people would describe the same way, which is exactly the kind of ambiguity that shows up later as low judge-human agreement with no clear reason why. A 0–2 scale forces each level to mean something a labeler can point to: 0 is a real failure, 1 is a specific, nameable imperfection, 2 is clean. Every level in `rubric.py` has a written description for exactly this reason — a labeler, human or an LLM judge, should never have to guess what a given number means.

## Why the golden set has deliberately flawed examples, not just good ones

A rubric that has only ever been tested on clean outputs has not actually been tested. The golden set's `billing-hallucinated` example exists specifically to check that `factual_accuracy` catches an invented claim, `billing-incomplete` exists to check that `coverage` catches an omission, and `indexing-wrong-format` exists to check that `format_adherence` catches a length violation that leaves accuracy and coverage untouched. Each flawed example is paired with a matching clean example on the same source, which is what makes `test_the_golden_set_contains_more_than_one_quality_level_per_source` a meaningful check rather than a formality — a golden set with no quality variation cannot validate that a rubric or a judge discriminates between good and bad output at all.

## Why an LLM judge needs an agreement check before it is trusted

An LLM judge that has never been checked against human labels is an unvalidated instrument. It might share the same blind spots as the model being evaluated, or score confidently while being systematically wrong about one criterion. `evaluate_agreement` exists to catch that before the judge's scores are trusted to generate preference data at a scale no human labeler could review by hand. A judge with strong agreement on `factual_accuracy` but weak agreement on `conciseness`, for instance, is a judge whose accuracy scores can be trusted and whose conciseness scores still need a human in the loop — that distinction is only visible per-criterion, which is why `evaluate_agreement` reports one row per criterion instead of a single blended number.
