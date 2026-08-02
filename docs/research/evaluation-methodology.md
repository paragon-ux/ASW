# Run Protocol

## Phase A — freeze

Before the first comparative run:

1. record target repository commit SHA and clean status;
2. validate extension schemas/fixtures;
3. finalize the machine-readable evaluation profile;
4. record Windows/ASW/runtime versions;
5. record probe/baseline implementation versions;
6. freeze poll intervals, deadlines, repetition counts, randomized-delay range, text-notification template, metrics, and thresholds.

Write the frozen profile to `evaluation/results/<run_id>/profile.json`. Never mutate it in place after trials begin.

## Layer A — deterministic systems benchmark

Default MVP repetitions:

- **20 repetitions per applicable primary scenario × condition**;
- **10 repetitions per secondary scenario × condition**.

This layer contains no LLM calls.

Randomize condition order within each scenario/repetition using the recorded run seed to reduce ordering bias.

## Integrity check

Before Layer B, require:

- ground-truth completeness = 100%;
- no observer can read the ground-truth private channel;
- no raw-result schema errors;
- deterministic aggregation reproduces the same summary from the same raw JSONL.

## Layer B — bounded agent continuation

To conserve model usage:

- primary scenarios only;
- ASW plus the mechanically selected best non-ASW baseline for each scenario;
- **3 repetitions per scenario × condition** by default;
- same fixed agent/model/tool configuration for both conditions;
- fixed maximum tool-call and token budgets;
- randomized condition order using a recorded seed.

Do not increase repetitions after seeing unfavorable results. A larger follow-up study is separate from the MVP gate.

## Finalization

1. seal raw results read-only where practical;
2. regenerate aggregate summary from raw JSONL;
3. validate result/summary schemas;
4. run the evaluation hard-gate audit;
5. write `docs/EVALUATION_RESULTS_<date>.md` with methodology, results, thresholds, failures, and final classification.
