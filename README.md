# memory-tripwires

Eight small, synthetic scenarios for mistakes an agent's memory can make. Sixteen questions with explicit grading criteria, plus a dependency-free tool to export a single probe without its answers or future messages.

**Not a leaderboard or a validated benchmark.** These are inspectable starter fixtures for debugging memory behavior. A documented exploratory Mem0 observation is included below; no overall quality ranking is claimed.

## One observed failure

On April 2, a user says they only checked an application status. In one configured Mem0 OSS smoke, extraction stored that activity as April 1. The retrieved-memory answer then said there was no information about April 2; the same answer model with the original dialogue identified the status check correctly.

[Read the example and inspect the synthetic evidence](examples/relative-date/README.md). It includes the exact answers, extraction output, model settings, and a significant limitation: the adapter's report timestamps and Mem0's own observation date used different years. This is a debugging example, not a general verdict on Mem0 or a benchmark score.

## What is inside

| Scenario | What it checks |
| --- | --- |
| Preference update | Apply the current preference without rewriting history |
| Event time | Distinguish when something happened from when it was reported |
| Relative date | Resolve “yesterday” against the original message |
| Context boundary | Keep a valid preference within its intended context |
| Tentative plan | Preserve uncertainty and separate similar events |
| Negated ownership | Keep subjects and explicit negation straight |
| Selective forgetting | Withhold a requested secret while retaining unrelated information |
| Derived vs source | Avoid promoting an observation into a stable personal preference |

Every case includes a second probe checking a related ability or a different point in the conversation. Inspect both results: success on one question must not hide failure on the other.

## Try it

Requires Python 3.9+; no packages, API keys, models, or services are needed for the fixture tool.

```sh
python3 tripwires.py
python3 tripwires.py --case preference-update --probe p1
python3 -m unittest discover -s tests -v
```

The first command validates the fixtures. The second exports a context prefix and question as JSON. It does not call a model or execute an experiment.

To try a memory system:

1. Start with fresh, isolated state for **each probe**, even when two probes share a case.
2. Ingest only the exported `turns`, in order. Preserve their `at` timestamps as report times. Do not ingest the case ID, question, grading criteria, or the entire dataset wrapper.
3. Ask the exported `question` after ingestion. If the system cannot ingest timestamps, record that limitation rather than silently removing time information.
4. Compare the answer against every `must` and `must_not` criterion for that probe in [the dataset](cases/scenarios.json). These are semantic criteria, not exact-string matches. Equivalent wording is acceptable.
5. Record the actual answer, case/probe IDs, dataset commit, system version, configuration, and any unavailable behavior. Report individual outcomes: PASS if all criteria hold, FAIL if one is violated, UNCLEAR if the answer cannot be judged, or UNSUPPORTED if the required operation is unavailable.

Do not feed earlier probe answers back into later probes. A plain-context control can receive the same exported prefix and question directly; that comparison alone does not isolate a memory mechanism's quality.

## Data format

`schema_version: 1`; `cases` contains records with:

- `id`, `category`, `limit`: identification and the interpretation boundary.
- `turns`: ordered user messages with `id`, UTC report timestamp `at`, `role`, and `text`.
- `probes`: `id`, `after_turn`, `question`, `must`, and `must_not`.

`after_turn` is an inclusive boundary. A probe sees that message and all previous messages, never later ones. Event dates mentioned inside a message may precede its report timestamp. All people, places, preferences, and secrets in the fixtures are fictional.

The tool validates fixture structure and boundaries. It does not grade model answers. Its seven tests cover export isolation, ambiguous or missing boundaries, report ordering, and source immutability.

## Important limits

The forgetting case checks **response-level compliance**, not physical deletion. The raw fixture intentionally contains the synthetic secret. An answer that withholds it proves nothing about deletion from storage, summaries, logs, or model weights. The natural-language forgetting request is the stimulus; document any system-specific deletion adapter separately.

The dataset is tiny, English-only, public, and easy to memorize. It does not test long histories, scale, persistence across restarts, adversarial extraction, cost, or latency. There are no measured performance claims and no automatic judge. Keep per-case failures visible rather than presenting a single quality score.

This repository supplies inputs and criteria, not a runner. It can be used manually or adapted to an experiment runner later; no Runloom integration is implemented here.

## Related

[handoff-check](https://github.com/Lopeloop/handoff-check) checks coding-agent handoffs against repository evidence.

Published by [Lopeloop](https://github.com/Lopeloop). MIT licensed, including the synthetic data.
