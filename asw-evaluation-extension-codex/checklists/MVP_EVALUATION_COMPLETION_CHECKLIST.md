# ASW MVP Evaluation Completion Checklist — Hard Gate

Evidence run: `evaluation/results/asw-mvp-eval-20260802-05`  
Aggregate: `evaluation/results/asw-mvp-eval-20260802-05/aggregate-summary.json`  
Report: `docs/EVALUATION_RESULTS_2026-08-02.md`

## Baseline protection

- [x] Target repository base commit is recorded and core worktree state is clean before extension changes — `docs/BASELINE_VERIFICATION.md`; final `run-manifest.json` repeats commit `7d6e267c6e89cdcd8a71644c67c95d2ab4260330` and `baseline_verification.core_worktree_clean=true`.
- [x] Existing implementation hard-gate checklist and runtime qualification are present and accepted — `asw-spec-codex/checklists/MVP_COMPLETION_CHECKLIST.md` and `asw-spec-codex/docs/RUNTIME_QUALIFICATION_2026-08-02.md`.
- [x] No ASW core product module or existing RFC schema was modified — extension-only diff; the ASW adapter imports committed public/service interfaces.

## Harness and ground truth

- [x] Controlled job success/failure probe exists — `evaluation/scenarios/controller.py`, `fixtures/scenarios/job-success.json`, `job-failure.json`.
- [x] Controlled external file/artifact probe exists — `evaluation/scenarios/controller.py`, `fixtures/scenarios/external-file-stable.json`, `artifact-ready.json`.
- [x] Controlled UI modal/control probe exists — `evaluation/scenarios/controller.py`, `fixtures/scenarios/modal-appears.json`, `operation-available.json`.
- [x] Secondary render/export and crash/restart probes run — Layer A records for `render-export` and `crash-restart`, each at the frozen 10 repetitions.
- [x] Scenario controller records independent monotonic ground truth inaccessible to benchmark observers — `ground-truth.jsonl`; `evaluation/tests/test_phase8.py::test_ground_truth_is_independent_from_observer_surface`.
- [x] Randomized delays/seeds are recorded and prevent fixed-timing shortcuts — per-trial `seed`, `random_delay_ms`, and `transition_ns` in `ground-truth.jsonl`.

## Baselines

- [x] Polling baseline is executable with frozen interval/budget — `evaluation/baselines/observers.py`, profile interval/deadline.
- [x] Filesystem-watch-only baseline is executable for applicable scenarios — `FilesystemWatchObserver`; non-file pairs are explicit `not_applicable` rows.
- [x] Ordinary-notification-text baseline uses a frozen plain-text contract — profile template and `OrdinaryNotificationObserver`.
- [x] Repeated-observation baseline is executable with frozen interval/budget — `RepeatedObservationObserver`; interval regression test.
- [x] ASW condition uses normal ASW public/service subscription/read/stream interfaces only — `CoreASWPublicClient` uses `ASWService.emit_event` and `AgentAPI.open_signal_stream`.
- [x] Non-applicable baseline/scenario pairs are recorded as `not_applicable` — raw trial JSONL includes all five condition rows per scenario/repetition.

## Frozen profile

- [x] Evaluation profile validates against `schemas/evaluation-profile.schema.json` — `python -m evaluation.validate`.
- [x] Base commit, environment, seed, repetitions, deadlines, polling interval, notification template, agent configuration, budgets, metrics, selection rule, and thresholds are frozen before comparative runs — `profile.json`, digest in `run-manifest.json`.
- [x] Frozen profile digest is recorded in the run manifest — `profile_digest` matches SHA-256 during validation and rebuild.
- [x] Thresholds are unchanged after the first comparative trial begins — invalidated runs document harness defects; final run uses the unchanged fixture thresholds.

## Layer A — deterministic systems benchmark

- [x] All primary scenario × applicable condition runs complete at the frozen repetition count — 20 repetitions per primary scenario and condition in raw JSONL.
- [x] Layer A contains no model/LLM calls — integrity `layer_a_model_calls=0`.
- [x] Raw ground-truth and trial JSONL are persisted — `ground-truth.jsonl`, `raw-results.jsonl`.
- [x] Raw results validate against schemas — `python -m evaluation.validate --run ...`.
- [x] Aggregation is deterministic and reproducible from raw results — repeated `python -m evaluation.aggregate` produces the same SHA-256 summary.
- [x] Detection latency, observation count, misses, duplicates, false positives, attribution, kind, subject, and continuation-readiness metrics are computed — aggregate Layer A tables.
- [x] Best non-ASW baseline is selected mechanically using the preregistered rule — `best_non_asw_baseline_by_scenario` and profile `selection_rule`.

## Layer B — bounded agent continuation

- [x] Layer B begins only after Layer A integrity checks pass — runner selects baselines only after complete/validated Layer A rows.
- [x] Each primary scenario compares ASW only with its mechanically selected best non-ASW baseline — `agent-usage.jsonl` and summary.
- [x] Exactly the frozen small repetition count is used — 3 repetitions per primary scenario × condition.
- [x] Agent/model/tool configuration is identical between compared conditions — profile agent block and identical prompt hash/configuration.
- [x] Tool calls, observation/read calls, continuation success, continuation latency, incorrect actions, and token usage are persisted — raw trial JSONL and `agent-usage.jsonl`.
- [x] No post-result prompt/budget tuning favors one condition — frozen profile digest and invalidation records.

## Threshold audit

- [x] ASW detection success >= 98% — aggregate `1.0`.
- [x] Duplicate useful-signal rate <= 2% — aggregate `0.0`.
- [x] False-positive useful-signal rate <= 2% — aggregate `0.0`.
- [x] Application attribution accuracy >= 98% where applicable — aggregate `1.0`.
- [x] Kind accuracy >= 98% — aggregate `1.0`.
- [x] No replay/access/authorization violation occurred — integrity counts are all `0`.
- [x] At least 2 of 3 primary classes show >= 30% median observation-count reduction without >2pp detection regression — all 3 pass at 50% reduction and 0pp regression.
- [x] Agent continuation success is not worse than selected baseline by >5pp — both are `1.0`.
- [x] Agent layer shows >=20% median observation-call or continuation-time improvement — 50% call and latency improvement.

## Evidence and claims

- [x] Run manifest, frozen profile, ground truth, raw results, aggregate summary, agent usage, and final report are persisted.
- [x] Final report includes negative/failed results and exclusions — invalidated technical runs and explicit not-applicable rows are documented.
- [x] Final classification is exactly `SUPPORTED`, `NOT_SUPPORTED`, or `INCONCLUSIVE` — `SUPPORTED`.
- [x] `SUPPORTED` is claimed only because every required threshold passes — `threshold_audit.pass=true`.
- [x] Final claim is limited to the bounded RFC 0001 MVP proposition — report claim-discipline section.
