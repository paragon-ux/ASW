# ASW Phase 8 Evaluation Results — asw-mvp-eval-20260802-05

Final classification: SUPPORTED

This report is derived from the frozen profile, independent ground-truth JSONL, raw trial JSONL, and deterministic aggregate. It supports only the bounded RFC 0001 MVP proposition.

## Repository and environment

- Base commit: 7d6e267c6e89cdcd8a71644c67c95d2ab4260330
- Profile digest: sha256:9c38bd41057e1933cda9c54c26fa143f775d7e6bbb5cd2848423ccd7cebeb1c7
- Frozen at: 2026-08-02T09:08:44Z
- Completed at: 2026-08-02T09:09:37Z
- Harness version: 1.0.0
- Host: Windows-10-10.0.22000-SP0 / Python 3.11.9
- Accepted runtime qualification: Windows 11 Pro build 22000 (Python reports the compatible Windows build string above).
- Core baseline status: True

## Hypothesis and frozen inputs

The hypothesis is that structured ASW signals reduce unnecessary observation/tool effort while preserving transition recognition and continuation. Layer A is model-free. Layer B uses exactly the preregistered three repetitions per primary scenario and the same normalized deterministic continuation-agent configuration in both conditions; no post-result prompt, budget, interval, or threshold tuning occurred. The bounded continuation agent is deterministic and normalized; this run makes no external LLM-call claim.

- Primary repetitions: 20; secondary repetitions: 10; Layer B repetitions: 3
- Poll interval/deadline: 250 ms / 15000 ms
- Random delay range and seed: {'max': 2000, 'min': 500} / 20260802
- Ordinary notification template: {application}: {plain_status_text}

## Scenario and baseline implementations

Controlled probes cover job success/failure, stable external file/artifact transitions, UI modal/control transitions, render/export-style output, and crash/restart. Ground truth is recorded by the controller before each condition and is not passed to observers. Polling, filesystem-watch-only, ordinary plain-text notification, repeated observation, and ASW conditions use the same scenario timeline; non-applicable pairs are persisted explicitly.

## Layer A results

| Scenario | Condition | Trials | Detection | Median observations | Median latency (ms) | Kind accuracy | Attribution |
|---|---|---:|---:|---:|---:|---:|---:|
| artifact-ready | asw | 20 | 100.0% | 1.00 | 0.00 | 100.0% | 100.0% |
| artifact-ready | filesystem_watch | 20 | 100.0% | 4.00 | 169.00 | 100.0% | 100.0% |
| artifact-ready | ordinary_notification | 20 | 100.0% | 2.00 | 0.00 | 100.0% | 100.0% |
| artifact-ready | polling | 20 | 100.0% | 4.50 | 169.00 | 100.0% | 100.0% |
| artifact-ready | repeated_observation | 20 | 100.0% | 4.50 | 169.00 | 100.0% | 100.0% |
| crash-restart | asw | 10 | 100.0% | 1.00 | 0.00 | 100.0% | 100.0% |
| crash-restart | filesystem_watch | 0 | 0.0% | n/a | n/a | n/a | n/a |
| crash-restart | ordinary_notification | 10 | 100.0% | 2.00 | 0.00 | 100.0% | 100.0% |
| crash-restart | polling | 10 | 100.0% | 6.50 | 49.00 | 100.0% | 100.0% |
| crash-restart | repeated_observation | 10 | 100.0% | 6.50 | 49.00 | 100.0% | 100.0% |
| external-file-stable | asw | 20 | 100.0% | 1.00 | 0.00 | 100.0% | 100.0% |
| external-file-stable | filesystem_watch | 20 | 100.0% | 4.00 | 95.50 | 100.0% | 100.0% |
| external-file-stable | ordinary_notification | 20 | 100.0% | 2.00 | 0.00 | 100.0% | 100.0% |
| external-file-stable | polling | 20 | 100.0% | 5.00 | 95.50 | 100.0% | 100.0% |
| external-file-stable | repeated_observation | 20 | 100.0% | 5.00 | 95.50 | 100.0% | 100.0% |
| job-failure | asw | 20 | 100.0% | 1.00 | 0.00 | 100.0% | 100.0% |
| job-failure | filesystem_watch | 0 | 0.0% | n/a | n/a | n/a | n/a |
| job-failure | ordinary_notification | 20 | 100.0% | 2.00 | 0.00 | 100.0% | 100.0% |
| job-failure | polling | 20 | 100.0% | 6.50 | 190.50 | 100.0% | 100.0% |
| job-failure | repeated_observation | 20 | 100.0% | 6.50 | 190.50 | 100.0% | 100.0% |
| job-success | asw | 20 | 100.0% | 1.00 | 0.00 | 100.0% | 100.0% |
| job-success | filesystem_watch | 0 | 0.0% | n/a | n/a | n/a | n/a |
| job-success | ordinary_notification | 20 | 100.0% | 2.00 | 0.00 | 100.0% | 100.0% |
| job-success | polling | 20 | 100.0% | 5.00 | 173.00 | 100.0% | 100.0% |
| job-success | repeated_observation | 20 | 100.0% | 5.00 | 173.00 | 100.0% | 100.0% |
| modal-appears | asw | 20 | 100.0% | 1.00 | 0.00 | 100.0% | 100.0% |
| modal-appears | filesystem_watch | 0 | 0.0% | n/a | n/a | n/a | n/a |
| modal-appears | ordinary_notification | 20 | 100.0% | 2.00 | 0.00 | 100.0% | 100.0% |
| modal-appears | polling | 20 | 100.0% | 5.00 | 53.50 | 100.0% | 100.0% |
| modal-appears | repeated_observation | 20 | 100.0% | 5.00 | 53.50 | 100.0% | 100.0% |
| operation-available | asw | 20 | 100.0% | 1.00 | 0.00 | 100.0% | 100.0% |
| operation-available | filesystem_watch | 0 | 0.0% | n/a | n/a | n/a | n/a |
| operation-available | ordinary_notification | 20 | 100.0% | 2.00 | 0.00 | 100.0% | 100.0% |
| operation-available | polling | 20 | 100.0% | 5.50 | 132.50 | 100.0% | 100.0% |
| operation-available | repeated_observation | 20 | 100.0% | 5.50 | 132.50 | 100.0% | 100.0% |
| render-export | asw | 10 | 100.0% | 1.00 | 0.00 | 100.0% | 100.0% |
| render-export | filesystem_watch | 10 | 100.0% | 4.00 | 178.00 | 100.0% | 100.0% |
| render-export | ordinary_notification | 10 | 100.0% | 2.00 | 0.00 | 100.0% | 100.0% |
| render-export | polling | 10 | 100.0% | 6.00 | 178.00 | 100.0% | 100.0% |
| render-export | repeated_observation | 10 | 100.0% | 6.00 | 178.00 | 100.0% | 100.0% |

### Best-baseline selection

The preregistered rule (highest detection, then lowest misses, then median observations, then median latency, then lexical ID) selected:

- file_artifact_transition -> ordinary_notification
- job_completion -> ordinary_notification
- ui_transition -> ordinary_notification

## Layer B continuation results

| Scenario class | Condition | Trials | Continuation success | Median observation calls | Median continuation latency (ms) |
|---|---|---:|---:|---:|---:|
| file_artifact_transition | asw | 6 | 100.0% | 1.00 | 20.00 |
| file_artifact_transition | ordinary_notification | 6 | 100.0% | 2.00 | 40.00 |
| job_completion | asw | 6 | 100.0% | 1.00 | 20.00 |
| job_completion | ordinary_notification | 6 | 100.0% | 2.00 | 40.00 |
| ui_transition | asw | 6 | 100.0% | 1.00 | 20.00 |
| ui_transition | ordinary_notification | 6 | 100.0% | 2.00 | 40.00 |

## Failures, exclusions, and integrity

- Ground-truth records: 158; unique IDs: 158; completeness: True.
- Agent-usage records: 36; completeness/configuration: True.
- Layer A model calls: 0.
- Authorization violations: 0; replay violations: 0.
- Invalidated runs are retained separately and excluded from this classification; their persisted invalidation records are listed below.

## Threshold audit

- Detection success: 100.0% vs minimum 98.0% — PASS
- Duplicate useful-signal rate: 0.0% vs maximum 2.0% — PASS
- False-positive useful-signal rate: 0.0% vs maximum 2.0% — PASS
- Attribution accuracy: 100.0% vs minimum 98.0% — PASS
- Kind accuracy: 100.0% vs minimum 98.0% — PASS
- Layer A observation reduction: 3 classes pass; required 2 — PASS
- Layer B continuation non-inferiority: delta 0.0% vs maximum 5.0% — PASS
- Layer B efficiency: call improvement 50.0%, latency improvement 50.0%; minimum 20.0% — PASS
- Integrity gate: PASS
- Final threshold gate: PASS

## Evidence paths

- Frozen profile: `asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-05/profile.json`
- Run manifest: `asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-05/run-manifest.json`
- Ground truth: `asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-05/ground-truth.jsonl`
- Raw trial results: `asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-05/raw-results.jsonl`
- Agent usage: `asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-05/agent-usage.jsonl`
- Aggregate summary: `asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-05/aggregate-summary.json`

## Reproducibility

    python -m evaluation.validate --run evaluation/results/asw-mvp-eval-20260802-05
    python ..\asw-documentation-release-codex\verify_frozen_evidence.py --evaluation-root .

A SUPPORTED result here is limited to this bounded controlled RFC 0001 MVP proposition; it does not establish universal application coverage, cross-platform behavior, or universal agent benefit.

- Invalidation records: `asw-evaluation-extension-codex/evaluation/results/asw-mvp-eval-20260802-01/INVALIDATED.md`; `...-02/INVALIDATED.md`; `...-03/INVALIDATED.md`; `...-04/INVALIDATED.md`.
- Core-defect audit: no reproducible core defect was recorded.
