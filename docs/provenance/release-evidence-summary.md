# Release-bound Phase 8 evidence summary

This sanitized summary is the public-release anchor for the accepted run. The
historical report and original manifest remain retained separately; they are
not rewritten. This file intentionally uses repository-relative artifact paths
and omits machine-local configuration paths.

## Accepted run

- Run: `asw-mvp-eval-20260802-05`
- Classification: `SUPPORTED`
- Core commit: `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`
- Profile digest: `sha256:9c38bd41057e1933cda9c54c26fa143f775d7e6bbb5cd2848423ccd7cebeb1c7`
- Host boundary: Windows 11 Pro build 22000, x64, CPython 3.11.9

## Frozen results

- Detection success: `100%`.
- Duplicate useful-signal rate: `0%`.
- False-positive useful-signal rate: `0%`.
- Application attribution accuracy: `100%` where applicable.
- Event-kind accuracy: `100%`.
- Primary efficiency gate: `3/3` classes passed.
- Median observation reduction: `50%` versus selected `ordinary_notification`.
- Layer B continuation success: `100%` for ASW and selected baseline.
- Layer B observation-call improvement: `50%`.
- Layer B continuation-latency improvement: `50%`.
- Layer A model calls: `0`.
- Raw trial records: `736`.
- Independent ground-truth records: `158`.
- Agent-usage records: `36`.
- Authorization violations: `0`.
- Replay violations: `0`.

The secondary crash/restart aggregate recorded ASW `subject_accuracy = 0.0`.
It did not invalidate the primary hard gate and is retained as a limitation.

## Reproduction artifacts

The complete frozen run is in the evaluation package under:

`evaluation/results/asw-mvp-eval-20260802-05/`

It contains the profile, original manifest, independent ground truth, raw
trial results, agent usage, aggregate summary, and validation inputs. Invalidated
runs `-01` through `-04` remain retained with their invalidation records and are
excluded from the accepted classification.
