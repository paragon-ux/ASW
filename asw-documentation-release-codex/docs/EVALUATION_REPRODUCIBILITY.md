# Evaluation reproducibility

The accepted Phase 8 run is `asw-mvp-eval-20260802-05`, based on core commit
`7d6e267c6e89cdcd8a71644c67c95d2ab4260330`, profile digest
`sha256:9c38bd41057e1933cda9c54c26fa143f775d7e6bbb5cd2848423ccd7cebeb1c7`,
and final classification `SUPPORTED`.

## Frozen evidence

- [Run manifest](../evidence/run-manifest.json)
- [Aggregate summary](../evidence/aggregate-summary.json)
- [Sanitized evaluation report](../evidence/EVALUATION_RESULTS_2026-08-02.md)
- [Frozen profile](../../asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-05/profile.json)
- [Full run directory](../../asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-05/)

The full run directory contains the frozen profile, manifest, independent
ground truth, raw trial results, agent usage, aggregate, and validation
inputs. The release documentation package carries the small manifest/aggregate
anchors; bulk JSONL remains in the evaluation package and is not copied into a
public documentation bundle without a path/secret audit.

## Reproduce the checks

From a source release or checkout, first acquire the configured origin at the
proposed release revision. If the origin is access-restricted, use the
corresponding `v0.2.0` source release archive.

```powershell
git clone https://github.com/paragon-ux/ASW.git ASW
Set-Location .\ASW
git checkout v0.2.0
```

The evaluation package must be present as the sibling directory
`asw-evaluation-extension-codex`; it is not a separately installed PyPI
dependency. Then run from that package:

```powershell
Set-Location .\asw-evaluation-extension-codex
python -m evaluation.validate
python -m unittest discover -s evaluation/tests -q
python -m evaluation.validate --run evaluation/results/asw-mvp-eval-20260802-05
python ..\asw-documentation-release-codex\verify_frozen_evidence.py --evaluation-root .
```

Do not invoke `python -m evaluation.aggregate` directly on the accepted run:
that command writes `aggregate-summary.json` in its argument directory. The
verification helper validates the accepted directory read-only, recomputes in
an isolated temporary copy, and compares the recomputed aggregate byte-for-byte
with the accepted and public aggregates.

The accepted evaluation used 20 Layer A repetitions per primary scenario,
10 per secondary scenario, and 3 Layer B repetitions per primary scenario.
Each primary class contains two primary scenarios, yielding 6 Layer B trials
per condition and class. Layer A used zero model calls. Layer B used the same
bounded deterministic/normalized continuation configuration in both conditions.
The frozen continuation contract assigns 1 observation call and 20 ms for the
structured ASW path, versus 2 calls and 40 ms for the plain-text notification
path. These are scripted protocol values, not independently measured OS
execution latency, and the run makes no external-LLM generalization claim.

For Layer B, the observation-count contract counts one ASW stream result or one
notification receipt-and-parsing operation. Subscription setup and controlled
event publication are excluded.

## Integrity and exclusions

The final run contains 736 raw trial records, 158 independent ground-truth
records, and 36 agent-usage records. Authorization and replay violations are
zero. Invalidated runs `asw-mvp-eval-20260802-01` through `-04` are retained in
the evaluation package with invalidation records and excluded from the final
classification; they were not silently rewritten or deleted.

The independent ground-truth channel is separate from the observer surfaces.
The mechanically selected best non-ASW baseline for all three primary classes
was `ordinary_notification`.

## Result boundary

The headline result is an empirical claim about the frozen controlled Windows
MVP protocol. It is not a product guarantee outside that protocol. See the
[claims matrix](CLAIMS_AND_EVIDENCE.md), [whitepaper](WHITEPAPER.md), and
[known limitations](KNOWN_LIMITATIONS.md).
