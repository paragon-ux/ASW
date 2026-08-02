# AGENTS.md — ASW Phase 9 documentation and release instructions

Complete **Phase 9: Documentation, Publication, and Release Readiness** for the already-completed ASW RFC 0001 MVP.

This phase starts after successful core implementation, Windows runtime qualification, and a `SUPPORTED` Phase 8 evaluation. The main risk is now inaccurate claims, confusing product documentation, incomplete release metadata, or accidental reopening of proven implementation—not missing product features.

## Non-negotiable baseline protection

- Treat committed ASW RFC 0001 implementation as accepted unless Phase 9 uncovers a concrete documentation-blocking contradiction.
- Treat `asw-mvp-eval-20260802-05` as the accepted Phase 8 empirical run.
- Do **not** modify reducer semantics, journal/replay behavior, source behavior, access-control semantics, GUI behavior, agent protocol behavior, or evaluation thresholds as part of documentation cleanup.
- Do not silently repair product behavior while writing docs.
- If documentation reveals a reproducible core defect, create a minimal issue/reproducer and classify the affected release item as blocked. Do not reopen broad implementation work in this phase.
- Prefer links to the normative RFC and source-of-truth schemas over duplicating normative text into multiple guides.
- Never change historical evidence files merely to make publication prose cleaner.

## Documentation truth hierarchy

Use this authority order:

1. `asw-spec-codex/RFC-0001.md` — normative semantics and scope;
2. schemas/tests/current implementation — concrete contract and shipped behavior;
3. completed MVP checklist/runtime qualification — implementation/runtime evidence;
4. Phase 8 frozen profile, run manifest, raw/aggregate results, and final report — empirical evidence;
5. Phase 9 docs — explanation only.

When two sources appear inconsistent, do not invent a reconciliation. Prefer the higher authority for semantics and report any genuine evidence contradiction explicitly.

## Claims discipline

Every material public claim must be one of:

- **Normative:** directly supported by RFC 0001;
- **Implemented:** supported by code/tests/completion evidence;
- **Runtime verified:** supported by the Windows runtime qualification;
- **Empirically supported:** supported by the frozen Phase 8 run;
- **Limitation/non-goal:** explicitly bounded by the RFC or evaluation report.

Avoid vague superlatives such as “best,” “dramatically faster,” “production proven,” “universal,” or “solves asynchronous desktop automation.”

For empirical results, preserve the controlled-scenario boundary and frozen numbers. Do not round or reframe numbers in a way that implies broader statistical certainty than the experiment supports.

## Model routing and usage discipline

Optimize for the **cheapest model that is well-matched to the work**, not merely the cheapest model capable of producing text. Phase 9 is intentionally asymmetric: most repository/release work is mechanical and belongs on Luna Max, while a small set of externally facing narrative artifacts benefit materially from Sol's writing, synthesis, and claim-discipline strengths.

Documentation volume alone is still not a reason to escalate. **Artifact role and reasoning/writing risk are.**

### Luna Max — mechanical and evidence-preparation workhorse

Use **Luna Max** for the majority of Phase 9 execution, including:

- repository inspection and documentation inventory;
- claims/evidence matrix construction and evidence extraction;
- schema/API/configuration example extraction from existing contracts;
- installation-command verification and troubleshooting reproduction;
- architecture fact extraction from the settled RFC;
- packaging metadata and version inventory;
- dependency/ignore-list/license inventory;
- changelog assembly from committed changes;
- citation/reference formatting and link maintenance;
- consistency edits after the substantive prose is settled;
- documentation tests, link checks, package-content checks, secret/path scans, and release validation;
- mechanical repository cleanup; and
- deterministic generation of empirical tables from frozen Phase 8 results.

Luna MAY prepare structured notes, outlines, evidence packets, and first-pass factual scaffolding for public documents, but it should not be the default final-authoring model for the high-leverage public narrative artifacts below.

### Sol Medium — default for externally facing narrative documentation

Use **Sol Medium** as the default authoring model for public-facing documentation where reader comprehension, positioning, explanation quality, or claim calibration materially matters, including:

- the root README's product explanation and positioning;
- quickstart and first-run narrative;
- the user guide;
- the agent integration guide;
- architecture overview prose intended for external readers;
- security/privacy/authority explanations beyond mechanical policy transcription;
- known-limitations and troubleshooting explanations where wording affects user expectations;
- release notes intended for public consumption;
- the whitepaper's main body, including motivation, architecture explanation, methodology, results interpretation, discussion, and limitations.

Also use Sol Medium when the current task materially depends on one or more of:

- resolving an apparent contradiction between the normative RFC and actual documented behavior;
- determining whether a public claim is stronger than the empirical evidence permits;
- security/privacy threat-boundary reasoning that is not already explicit in the RFC;
- licensing compatibility or attribution questions that cannot be resolved mechanically from dependency metadata;
- deciding whether a packaging/release change alters product authority or security semantics;
- interpreting a surprising Phase 8 result that materially affects a public claim;
- difficult reproducibility/methodology questions; or
- a materially important documentation task that Luna attempted once and did not resolve adequately.

Do not use Sol Medium to enumerate files, reformat citations, check links, scan dependencies, or perform other work a deterministic tool or Luna can do equivalently.

### Sol High — narrow publication-quality synthesis

Phase 9 permits **deliberate Sol High use without requiring a prior Sol Medium failure**, but only for a small number of publication-critical synthesis tasks where the model specialization is likely to improve the final artifact materially.

Use **Sol High** for:

- the whitepaper's final integrated synthesis and publication-quality revision, especially the abstract, central argument, results interpretation, discussion, limitations, and conclusion;
- a final claim-calibration pass over the whitepaper when subtle wording could overstate causality, generality, or empirical certainty; and
- optionally, one final pass over the root README's top-level product narrative if the README functions as the primary public introduction and the substantive facts/evidence are already frozen.

Do **not** use Sol High for:

- evidence gathering or table generation;
- formatting, cross-linking, citation plumbing, packaging boilerplate, changelog mechanics, or repository hygiene;
- repeated stylistic rewrites of already-clear prose;
- user-guide sections that are primarily procedural after the interaction model is settled; or
- any task that would cause a review/rewrite loop.

Prepare a compact evidence packet before a Sol High invocation so it can synthesize rather than rediscover. One strong publication pass is preferred over repeated refinement.

### Routing rule

Route by **artifact role plus reasoning risk**, not document size, token count, or number of files.

Use this default split:

```text
mechanical inspection / evidence extraction / validation -> Luna Max
public README / user docs / agent docs / explanatory architecture -> Sol Medium
whitepaper substantive drafting -> Sol Medium
whitepaper final integrated synthesis / claim calibration -> Sol High
mechanical cleanup after substantive prose is settled -> Luna Max
```

A long evidence table belongs on Luna. A short paragraph defining what the experiment actually proved belongs on Sol.

When multiple documentation structures are compliant, prefer the one with:

1. fewer duplicated facts;
2. fewer normative restatements;
3. fewer maintenance points;
4. fewer dependencies/tools;
5. fewer model calls;
6. easier link/evidence verification;
7. clearer reader journeys.

The objective is **selective specialization**: spend Sol usage on the small fraction of Phase 9 where public reasoning and prose quality matter most, while keeping the bulk of execution on Luna and deterministic tooling.

## Review-agent policy

The main agent owns documentation, repository changes, validation, fixes, packaging, and checklist evidence. **Do not orchestrate work through subagents.**

The only permitted delegated review is the existing repository **review-agent skill**.

Use at most **one review-agent pass per Phase 9 documentation phase**. Do not enter review loops.

Give the reviewer a compact packet:

- current documentation phase and intended audience;
- changed files/diff;
- relevant RFC/evidence pointers;
- current validation/link/package results;
- only the 2–3 highest-risk review categories.

Recommended review categories:

- Phase 9A: evidence fidelity, claim scope, information architecture;
- Phase 9B: user/agent clarity, security/privacy accuracy, installation reproducibility;
- Phase 9C: whitepaper methodology fidelity, result interpretation, limitation discipline;
- Phase 9D: packaging/release completeness, licensing/security disclosure, public-release hygiene.

Use Sol Medium for a reviewer only when the selected categories genuinely require claim/methodology/security/licensing reasoning. Otherwise use Luna.

After the single review, fix material findings, rerun affected checks, and continue. Do not request a second reviewer merely to confirm the fixes.

## Token and context efficiency

Treat usage as a constrained engineering resource.

- Read the Phase 9 core package once; then load only the repository docs/evidence relevant to the current slice.
- Prefer `git diff`, targeted search, headings, and file-specific inspection over rereading full RFC/evidence documents repeatedly.
- Create an evidence/claims matrix once and reuse it instead of re-deriving every number in every document.
- Do not paste large RFC sections into prompts when a path + section pointer is sufficient.
- Do not regenerate empirical tables manually when they can be derived from persisted aggregate results.
- Do not rerun Phase 8 merely to write documentation.
- Do not spend model tokens producing machine-computable inventories when a script can enumerate files, dependencies, links, licenses, or ignored artifacts.
- Run cheap deterministic validation frequently; use broader documentation/release audits only at phase boundaries.
- Avoid multiple stylistic rewrites once content is accurate and clear enough.

## Required public documentation surfaces

At minimum, Phase 9 should leave the repository with a coherent path for these audiences:

### New user

- root README;
- requirements/prerequisites;
- install/start instructions;
- first-run GUI journey;
- observation authorization versus subscription explanation;
- troubleshooting and known limitations.

### Agent integrator

- local agent protocol overview;
- grant/subscription/effective-scope model;
- list/read/stream/resume examples;
- cursor/revocation/error behavior;
- explicit statement that normal agent use does not require the CLI.

### Maintainer/contributor

- architecture overview pointing to the normative RFC;
- development/test commands;
- package layout;
- generated/derived state rules;
- contribution expectations;
- release process.

### Security/privacy reviewer

- local-only boundaries;
- observation authorization;
- agent access grants;
- server-side scope intersection;
- fail-closed semantics;
- UIA/filesystem/process observation boundaries;
- stored data/journal behavior;
- security reporting path.

### Research reader

- whitepaper;
- evaluation methodology;
- frozen run/result references;
- reproducibility instructions;
- limitations and non-goals.

## Whitepaper requirements

The whitepaper is an explanatory/research artifact, not a new normative spec.

It MUST:

- distinguish motivation/hypothesis from demonstrated results;
- describe ASW as a bounded deterministic Windows signaling system;
- explain observation authorization, canonical signals, subscriptions, and agent grants without reintroducing older actor/locus semantics;
- describe journal authority/replay and deterministic reduction at a useful architectural level;
- distinguish Windows notification delivery from canonical signals;
- describe the Phase 8 controlled transition methodology and independent ground truth;
- report frozen results exactly enough to reproduce the main tables;
- state that Layer A used zero model calls;
- state that the bounded Layer B continuation agent was deterministic/normalized and that the run makes no external-LLM generalization claim;
- preserve the controlled Windows MVP scope;
- include negative/secondary findings such as the crash/restart subject-accuracy result where relevant;
- include reproducibility and artifact references;
- avoid claiming universal agent benefit or general application coverage.

## Packaging/release discipline

Phase 9 may modify packaging and repository metadata only to make the completed MVP installable/releasable. It MUST NOT change runtime semantics to simplify packaging.

Audit at least:

- package metadata and version source;
- runtime/dev dependency declarations;
- Windows-specific prerequisites;
- source distribution/wheel inclusion/exclusion;
- `.gitignore` and other ignore lists;
- accidental inclusion of journals, tokens, local config, evaluation bulk results, caches, build outputs, or machine-specific paths;
- license file and dependency notices;
- security policy/reporting instructions;
- changelog/release notes;
- clean-checkout install/test path;
- tag/version consistency.

Do not create a release tag until the Phase 9 hard gate is complete.

## Security and secrets

- Never publish tokens, agent credentials, local authorization secrets, machine-specific personal paths, or raw local journals that may contain sensitive paths/data.
- Treat evaluation artifacts as publishable only after checking them for machine-local/user-identifying paths and secrets.
- Documentation examples MUST use obvious placeholders rather than real credentials.
- Do not weaken authentication/access-control behavior for easier examples.

## Testing and validation contract

Before Phase 9 is complete:

1. all documentation links and referenced repository paths must resolve where tooling permits;
2. documented install/test/validation commands must be checked from a clean or equivalent environment where feasible;
3. README quickstart must match actual product interfaces;
4. empirical numbers must match persisted aggregate evidence;
5. version strings must be internally consistent;
6. packaging inclusion/exclusion must be inspected;
7. secret/machine-path scans must be run over release-bound files;
8. licensing/security/release files required by the chosen publication scope must exist;
9. the whitepaper claims matrix must contain no unsupported material claim; and
10. the release-readiness checklist must contain concrete evidence for every checked item.

## Definition of done

Phase 9 is done when a new user can install and understand ASW, an agent developer can integrate without reading implementation code, a maintainer can reproduce tests/evaluation, a reviewer can understand authority/security boundaries, and a research reader can distinguish what RFC 0001 specifies from what Phase 8 empirically demonstrated.

Do not declare completion because the prose “looks polished.” Completion requires the release-readiness checklist and evidence-backed claim audit to pass.
