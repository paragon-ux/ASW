# ASW Phase 8 - Controlled Evaluation

The `evaluation/` tree is the public deterministic harness for the bounded RFC 0001 MVP proposition. It compares ASW with the preregistered baseline observers using independent scenario ground truth and a fixed continuation model.

This harness does not claim live operating-system transition coverage. Windows runtime qualification is documented separately in `docs/research/runtime-qualification.md`; Phase 8 uses controlled deterministic probe timelines through the committed ASW service, reducer, and agent boundary.

## Canonical layout

- `evaluation/profile.py` - frozen profile and repository manifest metadata.
- `evaluation/runner.py` - controlled run orchestration.
- `evaluation/baselines/` - polling, ordinary-notification, and repeated-observation baselines.
- `evaluation/consumers/asw_adapter.py` - public ASW service and agent API adapter.
- `evaluation/scenarios/` - scenario definitions and controlled probe surfaces.
- `evaluation/metrics.py` - deterministic aggregation, integrity checks, and threshold audits.
- `evaluation/schema.py` and `evaluation/schemas/` - evaluation document validation.
- `evaluation/fixtures/` - valid and intentionally invalid evaluation documents.
- `evaluation/tests/` - harness contract tests.
- `evaluation/results/asw-mvp-eval-20260802-05/` - the accepted release-bound
  profile, sanitized public run manifest, raw trials, ground truth, agent usage,
  and aggregate.
- `docs/provenance/` - sanitized release anchors and provenance.

## Scope and claim boundary

The evaluation is additive release evidence; it does not reopen or alter ASW
core semantics. Layer A uses zero model calls. Under the frozen Layer B
protocol, ASW counts one structured signal-stream read. The
ordinary-notification condition counts two observations: (1) notification
receipt and (2) parsing/interpretation. Subscription setup and controlled event
publication are excluded. The 20 ms and 40 ms continuation values are
normalized scripted protocol values, not independently measured Windows
execution latency.

The accepted run is `asw-mvp-eval-20260802-05`. Its public evidence is
available under `evaluation/results/asw-mvp-eval-20260802-05/` and anchored by
the accepted base commit, profile digest, aggregate hash, and record counts
recorded in `docs/provenance/accepted-run-manifest.json` and
`docs/provenance/accepted-aggregate.json`.

Claims remain limited to bounded controlled Windows MVP scenarios. The results do not establish universal application support, cross-platform validation, universal agent benefit, or general-purpose desktop understanding.

## Validation and execution

Run commands from the repository root. The evaluation works without `build-docs/` or any sibling construction workspace.

```text
python -m unittest discover -s evaluation/tests -p "test_*.py"
python -m evaluation.validate
python -m evaluation.validate --run evaluation/results/asw-mvp-eval-20260802-05
python tools/verify_frozen_evidence.py
python -m evaluation.run --help
```

The frozen release gate is run with the maintainer utility at `tools/verify_frozen_evidence.py`. It validates the accepted run without rewriting historical evidence or rerunning the comparative experiment.
