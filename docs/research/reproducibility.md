# Evaluation reproducibility

The accepted Phase 8 run is `asw-mvp-eval-20260802-05`, based on core commit `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`, profile digest `sha256:9c38bd41057e1933cda9c54c26fa143f775d7e6bbb5cd2848423ccd7cebeb1c7`, and classification `SUPPORTED`.

## Public evidence

- [Accepted run manifest](../provenance/accepted-run-manifest.json)
- [Accepted aggregate](../provenance/accepted-aggregate.json)
- [Canonical accepted run evidence](../../evaluation/results/asw-mvp-eval-20260802-05/)
- [Release evidence summary](../provenance/release-evidence-summary.md)
- [Evaluation results](evaluation-results.md)
- [Evaluation methodology](evaluation-methodology.md)

The accepted profile, independent ground truth, raw trial results, agent usage,
and aggregate are promoted byte-for-byte into the canonical run directory.
The historical source manifest contains machine metadata, including a local
configuration path, so it remains unchanged in the private construction/evidence
archive. The public run directory uses a schema-valid release-sanitized manifest
derived from the already-sanitized provenance manifest; it preserves the run ID,
base commit, profile digest, timestamps, host boundary, scenario/baseline
versions, and evidence paths without publishing workstation metadata.

## Validate a clean checkout

From the repository root of a `v0.1.0` checkout:

```powershell
python -m evaluation.validate
python -m evaluation.validate --run evaluation/results/asw-mvp-eval-20260802-05
python -m unittest discover -s evaluation/tests -q
python tools\validate_release.py
```

These commands validate the public harness, its schemas and fixtures, and the release-bound documentation/metadata without requiring `build-docs/` or a sibling checkout.

## Verify the accepted frozen aggregate

The release gate verifies the unchanged public evidence bundle directly from the
canonical repository:

```powershell
python tools\verify_frozen_evidence.py
```

The verifier checks the accepted run ID and base commit, profile digest, exact
hashes for the promoted immutable files, 736 raw trial records, 158
ground-truth records, and 36 agent-usage records. It validates the frozen run,
recomputes the aggregate in an isolated temporary copy, and compares the result
and SHA-256 with
`80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C`.

## Protocol boundary

The evaluation uses controlled deterministic transition timelines and independent
ground truth. Layer A used zero model calls. Layer B uses three repetitions per
primary scenario and a deterministic normalized continuation policy. Under the
frozen Layer B protocol, ASW counts one structured signal-stream read. The
ordinary-notification condition counts two observations: (1) notification
receipt and (2) parsing/interpretation. Subscription setup and controlled event
publication are excluded. The 20 ms and 40 ms continuation values are
normalized scripted protocol values, not independently measured Windows
execution latency.

Invalidated runs `asw-mvp-eval-20260802-01` through `-04` remain retained in the immutable evidence archive and are excluded from the accepted classification. Do not regenerate trials, change thresholds, or replace the accepted aggregate to obtain a different result.
