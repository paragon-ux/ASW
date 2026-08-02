# ASW Phase 9 Release Readiness Checklist - Hard Gate

Phase 9 sign-off date: 2026-08-02

Final classification: READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS

Every applicable hard-gate item below is signed off. The bounded Windows 11
scope, deterministic/scripted Layer B protocol, and secondary crash/restart
subject-accuracy result remain documented limitations, not release blockers.

## Evidence and claims

- [x] Core commit and accepted Phase 8 run are recorded in `PACKAGE.json`, `EVIDENCE_BASELINE.md`, and the sanitized release evidence anchors.
- [x] Public claims are classified in `docs/CLAIMS_AND_EVIDENCE.md` as normative, implemented, runtime verified, empirically supported, or limitation.
- [x] Every empirical headline number matches `evidence/aggregate-summary.json` and the accepted report.
- [x] The bounded controlled-scenario qualifier appears adjacent to major empirical claims in `README.md` and `docs/WHITEPAPER.md`.
- [x] No universal application, cross-platform, production-scale, or universal-agent claim is made; the validator rejects the known overclaim phrases.
- [x] The secondary crash/restart `subject_accuracy = 0.0` result is retained in the evidence summary, claims matrix, README, and whitepaper.

## Root documentation

- [x] Root README clearly states what ASW is and is not.
- [x] README states MVP status and links to RFC 0001, the sanitized evaluation report, and the whitepaper.
- [x] README states tested prerequisites and installation instructions.
- [x] README provides a short first-run/quickstart path.
- [x] README distinguishes observation authorization, signals, subscriptions, and delivery.
- [x] README points users, agents, maintainers, and researchers to the appropriate deeper docs.

## User and agent guides

- [x] User guide covers Activity, Subscriptions, Applications, Sources & Permissions, and Agents.
- [x] User guide explains permissions without exposing unnecessary internal bookkeeping.
- [x] Agent guide documents the implemented structured list/read/stream/resume behavior.
- [x] Agent guide documents the grant/subscription/authorization intersection and revocation.
- [x] Agent examples match implemented API/tests and use placeholders rather than credentials.

## Architecture and reproducibility

- [x] Architecture overview points to RFC 0001 as the normative source rather than duplicating it.
- [x] Journal authority, deterministic reducer, signal history, and delivery separation are accurately explained.
- [x] Runtime prerequisites and Windows App SDK requirements are documented from verified evidence.
- [x] Development and test commands are documented and were executed successfully.
- [x] Phase 8 reproduction commands and exact run/artifact paths are documented.
- [x] Invalidated runs and the final accepted run are distinguishable and retained by reference.

## Whitepaper

- [x] Whitepaper separates hypothesis, design, implementation evidence, and empirical evidence.
- [x] Controlled deterministic transition timelines and independent-ground-truth methodology are explained; the paper does not claim live OS transitions in Phase 8.
- [x] Layer A zero-model-call property is stated.
- [x] Layer B bounded deterministic/scripted-agent limitation is stated, including assigned rather than independently measured latency values.
- [x] Frozen results, selected baseline, repetition units, and observation-count contract are reported correctly.
- [x] Limitations/threats to validity include bounded Windows scope and the secondary crash/restart subject result.
- [x] Whitepaper contains source-revision and evaluation-package reproducibility references.
- [x] Whitepaper does not introduce new normative product requirements.

## Security/privacy

- [x] `SECURITY.md` provides the configured author security mailbox (`mailto:work.jlines@gmail.com`) and the optional GitHub Advisory route.
- [x] Security/privacy guide describes observation authorization and server-side agent scope enforcement.
- [x] Local journal, path, and application-metadata sensitivity is documented.
- [x] Revocation and fail-closed behavior are documented.
- [x] No documentation suggests subscriptions or agents can broaden observation authority.
- [x] Public release-bound files contain no tokens, credentials, or sensitive local journals; the release builder audits paths and credential-shaped text.

## Licensing

- [x] Project license is explicit MIT in `LICENSE`, README, `PACKAGE.json`, changelog, and release notes.
- [x] Copyright/ownership text consistently uses the configured repository identity `paragon-ux`; no third-party holder was invented.
- [x] Direct and transitive third-party dependencies are inventoried in `THIRD_PARTY_NOTICES.md`.
- [x] Required third-party notices/attributions are included.
- [x] No license compatibility question remains unresolved for the reviewed source release set.

## Packaging and repository hygiene

- [x] Package/version metadata has one coherent Phase 9 source in `PACKAGE.json`, with the sibling core version checked as `0.2.0`.
- [x] Runtime and development dependencies are separated into the qualified pin files and documented.
- [x] Windows/runtime prerequisites are represented accurately, including the separate Windows App Runtime prerequisite.
- [x] Required schemas and package data are included by the public source archive allowlist.
- [x] `.gitignore` and the release builder exclude caches, builds, secrets, local journals, machine output, logs, and generated UI Automation logs.
- [x] Sanitized reproducibility evidence anchors are included; raw evaluation JSONL and unsanitized reports remain a separate audited input.
- [x] A transient public-source archive inspection passed for 134 files with no excluded output, machine-path, or credential findings; no archive was retained.
- [x] Clean-checkout/equivalent install and smoke validation passed where feasible: core fixtures, 59 core tests, evaluation validation, 7 evaluation tests, and the package validator.

## Clarity and consistency

- [x] Canonical terminology matches RFC 0001 (`signal`, `application`, `subscription`, `agent access grant`, `observation authorization`, `frontier`, `delivery`).
- [x] No obsolete WEN/Cues/Loci/actor-relevance terminology remains in public ASW docs.
- [x] No stale machine-specific absolute paths appear in public documentation/evidence intended for release.
- [x] Documentation links resolve under the deterministic package validator.
- [x] Examples are internally consistent and executable or explicitly illustrative.
- [x] Known limitations are centralized in `docs/KNOWN_LIMITATIONS.md` and linked from the public docs.

## Release metadata

- [x] Changelog contains the MVP release candidate entry.
- [x] Release notes summarize implementation proof and the Phase 8 empirical result without overclaiming.
- [x] Proposed version `0.2.0` and Git tag `v0.2.0` are recorded consistently; no tag was created or pushed.
- [x] Release artifact and SHA-256 procedures are documented and exercised on a transient audited archive.
- [x] Final release candidate source set contains no unintentional generated/local files under the public archive allowlist.

## Final review

- [x] Exactly one targeted review-agent pass was completed for each Phase 9 phase actually performed: 9A evidence/claims, 9B public documentation, 9C whitepaper synthesis, and 9D release hygiene.
- [x] Material findings from those four passes were fixed without entering review loops.
- [x] Final deterministic documentation, package, security, and license checks pass.
- [x] Final classification is `READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS`.

## Sign-off evidence

- Package validator: `python validate_package.py` -> `OK: Phase 9 release package validates (39 required files, 11 frozen evidence checks, links resolved)`.
- Frozen-evidence gate: `python verify_frozen_evidence.py --evaluation-root ..\asw-evaluation-extension-codex` -> accepted aggregate reproduced byte-for-byte; SHA-256 `80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C`.
- Core validation: `python validate_fixtures.py` -> `OK`; `python -m unittest discover -s tests -q` -> 59 tests, `OK`.
- Evaluation validation: `python -m evaluation.validate --run evaluation/results/asw-mvp-eval-20260802-05` -> validated run; `python -m unittest discover -s evaluation/tests -q` -> 7 tests, `OK`.
- Public artifact validation: `build_release_artifact.py` -> 134 audited files with a SHA-256 emitted by the builder; output was not retained in the workspace or release package.
- Licensing/security evidence: `LICENSE`, `PACKAGE.json`, `THIRD_PARTY_NOTICES.md`, and `SECURITY.md`.
- Claims/evidence evidence: `docs/CLAIMS_AND_EVIDENCE.md`, `evidence/aggregate-summary.json`, `evidence/RELEASE_EVIDENCE_SUMMARY.md`, and `evidence/RELEASE_RUN_MANIFEST.json`.
