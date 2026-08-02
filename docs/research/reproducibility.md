# Evaluation reproducibility

The accepted Phase 8 run is `asw-mvp-eval-20260802-05`, based on core commit `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`, profile digest `sha256:9c38bd41057e1933cda9c54c26fa143f775d7e6bbb5cd2848423ccd7cebeb1c7`, and classification `SUPPORTED`.

## Public evidence

- [Accepted run manifest](../provenance/accepted-run-manifest.json)
- [Accepted aggregate](../provenance/accepted-aggregate.json)
- [Release evidence summary](../provenance/release-evidence-summary.md)
- [Evaluation results](evaluation-results.md)
- [Evaluation methodology](evaluation-methodology.md)

The original frozen profile, manifest, independent ground truth, raw trial results, agent usage, and aggregate were verified byte-for-byte before construction-workspace archival. The original manifest contains machine metadata, so the immutable raw bundle is retained in the release engineering evidence archive and is not included in the public artifact. The sanitized manifest and aggregate preserve the accepted run ID, base commit, profile digest, counts, metrics, thresholds, and classification.

## Validate a clean checkout

From the repository root of a `v0.1.0` checkout:

```powershell
python -m evaluation.validate
python -m unittest discover -s evaluation/tests -q
python tools\validate_release.py
```

These commands validate the public harness, its schemas and fixtures, and the release-bound documentation/metadata without requiring `build-docs/` or a sibling checkout.

## Verify the accepted frozen aggregate

The release gate uses the unchanged raw evidence bundle supplied separately to the release engineer:

```powershell
python tools\verify_frozen_evidence.py --evaluation-root <immutable-evidence-bundle>
```

The verifier checks the accepted run ID and base commit, profile digest, 736 raw trial records, 158 ground-truth records, and 36 agent-usage records. It validates the frozen run, recomputes the aggregate in an isolated temporary copy, and compares the result and SHA-256 with `80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C`. It never writes to the supplied evidence bundle.

## Protocol boundary

The evaluation uses controlled deterministic transition timelines and independent ground truth. Layer A used zero model calls. Layer B uses three repetitions per primary scenario and a deterministic normalized continuation policy. The one-versus-two observation-count result counts one ASW structured-stream result versus one notification receipt-and-parsing operation; subscription setup and controlled event publication are excluded. The 20 ms and 40 ms continuation values are scripted protocol values, not independently measured Windows execution latency.

Invalidated runs `asw-mvp-eval-20260802-01` through `-04` remain retained in the immutable evidence archive and are excluded from the accepted classification. Do not regenerate trials, change thresholds, or replace the accepted aggregate to obtain a different result.
