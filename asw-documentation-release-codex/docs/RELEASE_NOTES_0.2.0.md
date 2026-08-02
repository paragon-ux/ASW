# ASW 0.2.0 MVP release candidate

Proposed Git tag: `v0.2.0`. License: MIT; copyright holder: `paragon-ux`.

ASW RFC 0001 is a bounded Windows 11 MVP. The release candidate adds the
publication surface needed for a new user, agent integrator, maintainer,
security/privacy reviewer, and research reader to understand and reproduce the
accepted implementation and evaluation.

The accepted core commit is `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`.
Windows runtime qualification covered native Windows App SDK delivery,
registered process/job transitions, UI Automation observations with physical
coordinates, the five-page GUI journey, the filesystem-to-agent flow, grant
revocation, and degradation/reconciliation recovery.

The accepted Phase 8 run is `asw-mvp-eval-20260802-05`, classified `SUPPORTED`.
In the preregistered controlled Windows MVP scenarios it achieved 100%
detection, 0% duplicate and false-positive useful-signal rates, 3/3 primary
classes at 50% median observation reduction versus `ordinary_notification`,
and 100% Layer B continuation success with 50% lower median observation calls
and continuation latency.

These are controlled-scenario empirical results, not universal application,
cross-platform, production-scale, or arbitrary-agent guarantees. Layer A used
zero model calls; Layer B used a bounded deterministic/normalized continuation
agent. The secondary crash/restart ASW `subject_accuracy = 0.0` result remains
visible in the whitepaper and evidence report.

The release does not create or push `v0.2.0`; maintainers should do so only
after the final checklist, license, security contact, and artifact inspection
are signed off.
