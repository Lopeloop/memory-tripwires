# Observed example: a date changed before retrieval

One synthetic debugging observation using Mem0 OSS and `relative-date / p2`.
The source-prefix control answered correctly; the retrieved-memory answer
could no longer identify the activity on the requested day.

## Input

| Report timestamp | User message |
| --- | --- |
| 2030-04-01 12:00 UTC | Yesterday, March 31, I submitted my application. |
| 2030-04-02 12:00 UTC | Today I only checked its status; I did not submit another application. |

Question: **What did I do on April 2?**

The expected detail is the application status check. Both messages were
in the permitted prefix; no later messages or grading criteria were ingested.

## What was observed

During extraction of the second message, the model emitted:

> User checked the status of their application on April 1, 2030, and did not submit a new application that day

The subsequently stored and retrieved entry also said **April 1**, even though
its `report_at` metadata still said **April 2**. The relevant entry was retrieved;
the failure was not simply a missed search result.

The final answer based on retrieved memory was:

> There is no information about your activities on April 2 in the provided context.

With the complete allowed source prefix, the same answer model and instruction
prompt produced:

> On April 2, you checked the status of your application but did not submit another application.

[Inspect the synthetic inputs, extraction output, stored/retrieved context,
answer instruction, configuration and exact final answers](observed.json).
The quotes above are generated outputs from this observation.

## Configuration and interpretation

- Mem0 OSS `2.2.1`, source snapshot
  [`f1791daa86d469249c9b002f62644d58a1eb96a0`](https://github.com/mem0ai/mem0/tree/f1791daa86d469249c9b002f62644d58a1eb96a0).
- `gpt-4.1-mini-2025-04-14` for extraction/update and final answers;
  `text-embedding-3-small`, 1536 dimensions. Temperature 0, top_p 1,
  max_tokens 600; default Mem0 infer=True extraction/update prompts.
- Fresh local Qdrant/SQLite state for this probe. Search top_k=20,
  threshold=0, rerank=False. No raw conversation in the memory-arm
  final-answer context; only retrieved entries and exposed metadata.
- A bounded synchronous REST transport was used for provider calls;
  Mem0's extraction/update/search logic and prompts were not changed.
  This is a configured memory-plus-answer pipeline, not a vendor benchmark
  or the managed Platform.

**Important temporal limitation:** this OSS snapshot does not accept native
`timestamp=` ingestion. The adapter prefixed each message with
`[Reported at <UTC timestamp>]` and stored the timestamp in metadata.
Mem0's extraction prompt also supplied **2026-11-10** as its own
Current Date and Observation Date, while the fixture's dates are in **2030**.
The input therefore contains competing temporal cues. This observation does
not isolate their effect from the model's handling of the report timestamps.

The narrow finding is that a date changed in this particular pipeline before
retrieval and the source-prefix control retained the answer. It is not a claim
that every Mem0 configuration fails temporal reasoning, or that memory
necessarily makes answers worse.

## Try the fixture yourself

From the repository root:

```sh
python3 tripwires.py --case relative-date --probe p2
```

This exports the exact permitted source prefix and question without the oracle.
Follow the [repository protocol](../../README.md#try-it) with your chosen
memory system, and keep the source-prefix control. For a comparable setup,
use the configuration and exact answer instruction in `observed.json` and
record how your adapter handles both report time and observation time.

This command does not execute Mem0 or reproduce the recorded API calls by
itself. This example ships an inspectable observation, not a one-command
Mem0 integration. A consistent observation-date adapter would be a separate
experiment; do not silently change it and overwrite the original observation.

## Evidence limits

This probe was completed once, before an unrelated request-byte budget stop
later in the larger smoke. Completed probes were not rerun; an explicitly
recorded continuation handled only the unanswered suffix. Manual assessment
was non-blind. No repeatability, statistical accuracy, or overall system
ranking is claimed. This is one selected failure example, not the full smoke
report. The excerpt contains synthetic data only; credentials, local machine
paths, provider request identifiers and unrelated project artifacts are omitted.
