# ASW Phase 9 — One-Shot Documentation and Release Kickoff

Continue from the committed, completed ASW RFC 0001 MVP. Your task is **documentation, publication, packaging/release hygiene, and the empirical whitepaper**. Do not reopen Phases 1–8 or alter product semantics.

Read first:

1. this package's `AGENTS.md`;
2. `EVIDENCE_BASELINE.md`;
3. `PHASE-9-DOCUMENTATION-AND-RELEASE.md`;
4. `checklists/RELEASE_READINESS_CHECKLIST.md`;
5. `docs/CLAIMS_AND_EVIDENCE.md`;
6. `docs/DOCUMENTATION_INFORMATION_ARCHITECTURE.md`;
7. `docs/WHITEPAPER_SPEC.md`.

Then inspect the target repository's committed `asw-spec-codex/RFC-0001.md`, current README/docs/package metadata, completed MVP/runtime evidence, and Phase 8 final evidence. Load only the files needed for the current Phase 9 slice.

## Baseline

Accepted core commit:

`7d6e267c6e89cdcd8a71644c67c95d2ab4260330`

Accepted evaluation run:

`asw-mvp-eval-20260802-05`

Accepted Phase 8 classification:

`SUPPORTED`

Do not rerun Phase 8 merely to write documentation. Do not modify historical evidence or thresholds.

## Objective

In one continuous run, make the repository ready for an MVP release candidate by completing Phases 9A–9D:

### 9A — Evidence map and documentation architecture

- inventory current docs;
- build a claims/evidence map;
- identify stale/duplicated terminology;
- establish canonical documentation homes;
- preserve RFC 0001 as normative source.

Use one targeted review-agent pass at phase end, maximum, focused on evidence fidelity, claim scope, and information architecture.

### 9B — Product and integration documentation

Create/update the smallest coherent public set needed for:

- README;
- installation/prerequisites;
- quickstart/first run;
- user guide;
- agent integration guide;
- architecture overview;
- security/privacy/authority guide;
- troubleshooting/known limitations;
- contributor/developer/reproducibility documentation.

Documentation must match actual code/tests. Do not invent API payloads or configuration flags.

Use one targeted review-agent pass at phase end, maximum, focused on user/agent clarity, security/privacy accuracy, and install reproducibility.

### 9C — Whitepaper

Create a polished `docs/WHITEPAPER.md` using the RFC and frozen evidence. Start from the supplied whitepaper specification/draft, but verify every technical statement against the target repository.

The paper must report the bounded result exactly enough to reproduce the headline:

- 100% detection;
- 0% duplicate and false-positive useful-signal rates;
- 3/3 primary classes at 50% median observation reduction versus selected baseline;
- Layer B 100% continuation success;
- 50% median observation-call and continuation-latency improvement;
- no Layer A model calls;
- accepted run `asw-mvp-eval-20260802-05`;
- bounded-scope limitations.

Preserve the secondary crash/restart subject-accuracy result rather than hiding it.

Use one targeted review-agent pass at phase end, maximum, focused on methodology fidelity, result interpretation, and limitation discipline.

### 9D — Release hygiene/pre-commit gate

Audit and fix only release/documentation concerns:

- packaging metadata/version source;
- dependencies and Windows prerequisites;
- `.gitignore` and package exclusions;
- secrets/local journals/machine-specific path leakage;
- licensing and third-party notices;
- `SECURITY.md`;
- changelog/release notes;
- clean-checkout install/test documentation;
- release artifact contents;
- proposed version/tag consistency;
- broken links and stale terminology.

Do not create/push the final Git tag unless explicitly asked. Produce the proposed tag/version and commands instead.

Use one targeted review-agent pass at phase end, maximum, focused on release completeness, licensing/security disclosure, and public hygiene.

## Efficiency and model specialization

Follow `AGENTS.md` strictly:

- use Luna Max for mechanical repository work, evidence extraction, deterministic tables, packaging/release hygiene, validation, and final mechanical cleanup;
- use Sol Medium for externally facing narrative documentation, including the README product narrative, user/agent guides, explanatory architecture/security prose, and substantive whitepaper drafting;
- use Sol High narrowly for the whitepaper's final integrated synthesis/claim-calibration pass and, only if useful, one final top-level README narrative pass;
- prepare compact evidence packets before Sol calls so Sol synthesizes rather than rediscovers;
- no subagent orchestration;
- no review loops;
- use scripts for link/file/dependency/license/secret/path inventories instead of spending model tokens on mechanical checks;
- do not repeatedly reread RFC/evaluation files;
- do not restate normative text where links/section pointers are clearer;
- do not polish already-clear prose repeatedly.

## Completion

Before finishing:

1. run all deterministic documentation/package checks available;
2. verify all empirical numbers against the frozen aggregate;
3. verify no machine-specific personal paths/secrets leak into intended public artifacts;
4. verify release packaging includes required schemas/docs and excludes local/generated state;
5. audit every item in `checklists/RELEASE_READINESS_CHECKLIST.md` with concrete evidence;
6. fix material release/documentation issues;
7. do not reopen implementation for subjective improvements.

Return one concise final report with:

- documentation created/updated;
- whitepaper status and evidence references;
- packaging/security/license/repository hygiene changes;
- deterministic checks and results;
- proposed release version/tag;
- checklist status;
- any exact blocking release issue.

Final classification must be one of:

`READY FOR MVP RELEASE`

`READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS`

`BLOCKED — RELEASE ISSUE`

Begin work immediately. Do not return a plan as the deliverable.
