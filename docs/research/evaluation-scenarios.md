# Controlled Scenarios

## S1 — Job completion/failure

The controller launches a registered probe job after a randomized delay.

Variants:

- exit 0 → expected `job.completed`;
- nonzero exit → expected `job.failed`;
- optional stable artifact emitted after work → expected `artifact.available` when applicable.

Ground truth records launch, completion, exit status, artifact stable time, application ID, and job ID.

## S2 — External stable file/artifact change

The probe performs a burst of writes to an authorized file/artifact, then stops writing.

Expected behavior is recognition of the stable useful transition rather than every raw write.

Ground truth records first write, final write, stable state, path/artifact identity, and digest when used.

## S3 — UI modal/control transition

A registered probe window appears. After a randomized delay it either:

- presents a modal/dialog; or
- changes a registered control from unavailable/disabled to available/enabled.

Ground truth records window identity, transition type, transition time, and expected application association. UI coordinates are evaluated only for the ASW condition because the baseline contract may not provide structured localization.

## S4 — Render/export-style artifact production (secondary)

Use `job_probe` with a render/export label and delayed artifact generation. This validates operation labeling plus artifact readiness without adding a third-party dependency.

## S5 — Crash/restart (secondary)

Launch `crash_probe`, cause controlled abnormal termination, then optionally restart the registered executable. Ground truth records start, crash, restart, PIDs, and application ID.

## Scenario integrity

Observers must not know the randomized transition delay in advance and must not read the controller's ground-truth channel.
