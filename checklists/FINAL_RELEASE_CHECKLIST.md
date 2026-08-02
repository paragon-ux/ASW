# ASW Final Repository Normalization and Release Checklist — Hard Gate

This checklist governs the final normalization, public-release, commit, and tag pass for **ASW — Application Signals for Windows, RFC 0001**.

The release MUST NOT be tagged while any required item below is unchecked.

Accepted anchors:

- Phase 8 run: `asw-mvp-eval-20260802-05`
- Evaluated core commit: `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`
- Accepted aggregate SHA-256: `80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C`
- Intended release version: `v0.1.0`

For every checked item, record concrete evidence in the item text, release report, or a stable repository-relative evidence file.

---

## 1. Scope protection

- [x] No ASW core semantic change was made during this release pass.
- [x] Reducer behavior was not changed.
- [x] Journal/replay behavior was not changed.
- [x] Observation-source behavior was not changed.
- [x] Authorization, grant, or effective-scope semantics were not changed.
- [x] Signal semantics were not changed.
- [x] GUI behavior was not changed merely to make documentation true.
- [x] Agent protocol behavior was not changed merely to make documentation true.
- [x] Phase 8 thresholds or frozen experimental inputs were not changed.
- [x] No new reproducible core defect was discovered. If one was discovered, release is `BLOCKED — RELEASE ISSUE` and `CORE REOPEN REQUIRED` is recorded.

## 2. Canonical source inventory

- [x] Current repository contents were inventoried before promotion/moves.
- [x] Accepted source location for the production package was identified.
- [x] Accepted source location for tests was identified.
- [x] Accepted source location for schemas was identified.
- [x] Accepted source location for fixtures was identified.
- [x] Accepted canonical RFC source was identified.
- [x] Accepted final documentation sources were identified.
- [x] Accepted evaluation assets intended for publication/reproduction were identified.
- [x] Accepted release/evidence tools intended for maintainers were identified.
- [x] No normative or empirical artifact was recreated from memory when an accepted source existed.

## 3. Canonical repository promotion

- [x] Production package is present at root `asw/`.
- [x] Product/conformance tests are present at root `tests/`.
- [x] Canonical schemas are present at root `schemas/`.
- [x] Canonical fixtures are present at root `fixtures/`.
- [x] Canonical RFC 0001 is present at `docs/rfc/RFC-0001.md`.
- [x] Intended public evaluation harness/assets are present under root `evaluation/`.
- [x] Intended maintainer/release/evidence utilities are present under root `tools/`.
- [x] Reviewed public documentation has been promoted into the canonical `docs/` tree.
- [x] Root release files have been promoted into canonical root locations.
- [x] Promotion copied only intended canonical/public artifacts; entire construction workspaces were not blindly copied into the public tree.

## 4. Canonical documentation tree

- [x] `docs/README.md` exists and is the canonical documentation index.
- [x] `docs/getting-started/installation.md` exists.
- [x] `docs/getting-started/quickstart.md` exists.
- [x] `docs/guides/user-guide.md` exists.
- [x] `docs/guides/agent-integration.md` exists.
- [x] `docs/guides/troubleshooting.md` exists.
- [x] `docs/reference/architecture.md` exists.
- [x] `docs/reference/agent-api.md` exists.
- [x] `docs/reference/signals-and-events.md` exists.
- [x] `docs/reference/security-and-privacy.md` exists.
- [x] `docs/reference/limitations.md` exists.
- [x] `docs/research/WHITEPAPER.md` exists and is canonical.
- [x] `docs/research/evaluation-methodology.md` exists.
- [x] `docs/research/evaluation-results.md` exists.
- [x] `docs/research/runtime-qualification.md` exists.
- [x] `docs/research/reproducibility.md` exists.
- [x] `docs/provenance/phase-9-mitigation-report.md` exists.
- [x] Sanitized Phase 9 review records are present under `docs/provenance/reviews/`.

## 5. Canonical-document uniqueness

- [x] Exactly one canonical public RFC 0001 exists.
- [x] Exactly one canonical installation guide exists.
- [x] Exactly one canonical quickstart exists.
- [x] Exactly one canonical user guide exists.
- [x] Exactly one canonical agent integration guide exists.
- [x] Exactly one canonical architecture reference exists.
- [x] Exactly one canonical security/privacy reference exists.
- [x] Exactly one canonical whitepaper exists.
- [x] Exactly one canonical evaluation methodology document exists.
- [x] Exactly one canonical evaluation-results document exists.
- [x] Exactly one canonical runtime-qualification document exists.
- [x] Exactly one canonical reproducibility guide exists.
- [x] No public documentation links to a competing construction-workspace copy.

## 6. Root README and documentation navigation

- [x] Root `README.md` names **ASW — Application Signals for Windows**.
- [x] Root README gives a concise product description.
- [x] Root README states the supported Windows target.
- [x] Root README states RFC 0001 MVP status accurately.
- [x] Root README describes the bounded empirical result without overstating it.
- [x] Root README provides a direct installation/quickstart path.
- [x] Root README includes a short architecture explanation.
- [x] Root README links to `docs/README.md`.
- [x] Root README links to user and agent guides.
- [x] Root README links to RFC 0001.
- [x] Root README links to whitepaper/evaluation material.
- [x] Root README links to security information.
- [x] Root README identifies the MIT license.
- [x] Root README does not require readers to understand Phase 1–9 construction history.
- [x] `docs/README.md` links only to canonical documentation paths.

## 7. Public-path sanitization

- [x] Public/packaged files contain no `C:\Users\<name>\...` paths.
- [x] Public/packaged files contain no `C:/Users/<name>/...` paths.
- [x] Public/packaged files contain no developer Desktop/workspace paths.
- [x] Public/packaged files contain no AppData paths.
- [x] Public/packaged files contain no temporary-directory paths that are meaningful only on the development machine.
- [x] Public/packaged files contain no virtual-environment paths that are meaningful only on the development machine.
- [x] Public/packaged files contain no usernames or machine names embedded in release paths.
- [x] Public Markdown links do not depend on sibling construction workspaces.
- [x] Public Markdown links do not point into `build-docs/`.
- [x] Public Markdown links do not point into any top-level `*-codex/` construction path.
- [x] Repository-contained references use repository-relative paths where possible.
- [x] External references use canonical public URLs where appropriate.
- [x] Evidence references use stable run IDs, commit SHAs, hashes, or filenames rather than workstation paths.
- [x] `<repo-root>` is used only where a concrete repository-relative example cannot express the instruction clearly.

## 8. Immutable historical evidence protection

- [x] No immutable Phase 8 raw evidence was rewritten solely for path cleanup or presentation.
- [x] No Phase 8 run ID was changed.
- [x] No Phase 8 base commit was changed.
- [x] No frozen profile digest was changed.
- [x] No accepted evidence hash was changed.
- [x] No frozen record count was changed.
- [x] No accepted metric was changed.
- [x] No threshold was changed.
- [x] No accepted classification was changed.
- [x] Historical artifacts containing local paths were either preserved unchanged outside the public artifact or represented by a sanitized derived summary/reference.
- [x] `.gitattributes` marks promoted accepted evidence as non-text so Windows checkouts preserve its bytes.
- [x] Accepted profile, ground truth, raw trials, agent usage, and aggregate are promoted byte-for-byte under `evaluation/results/asw-mvp-eval-20260802-05/`.
- [x] The public run manifest is a schema-valid sanitized equivalent; the historical manifest containing workstation metadata remains unchanged in the ignored archive.

## 9. Provenance preservation

- [x] Phase 9A review findings are preserved in sanitized form.
- [x] Phase 9B review findings are preserved in sanitized form.
- [x] Phase 9C review findings are preserved in sanitized form.
- [x] Phase 9D review findings are preserved in sanitized form.
- [x] Final Phase 9 mitigation report is preserved in sanitized form.
- [x] Finding IDs are preserved.
- [x] Severities are preserved.
- [x] Substantive finding text is preserved.
- [x] Mitigations are preserved.
- [x] Verification outcomes are preserved.
- [x] Relevant run IDs, commit SHAs, and deterministic hashes are preserved.
- [x] Resolved but inconvenient findings were not deleted.
- [x] Local-only links in provenance were replaced with canonical repository-relative references.

## 10. Construction-workspace archival

- [x] `asw-spec-codex/` was moved under `build-docs/asw-spec-codex/` after promotion completed.
- [x] `asw-evaluation-extension-codex/` was moved under `build-docs/asw-evaluation-extension-codex/` after promotion completed.
- [x] `asw-documentation-release-codex/` was moved under `build-docs/asw-documentation-release-codex/` after promotion completed.
- [x] Local construction archives were preserved rather than deleted unnecessarily.
- [x] Root `.gitignore` contains exactly the required `/build-docs/` ignore rule for the construction archive.
- [x] `build-docs/` is not part of the intended release commit.
- [x] `build-docs/` is not part of the public release artifact.
- [x] Public documentation contains no dependency on `build-docs/`.
- [x] Runtime/test/evaluation/release tooling contains no dependency on `build-docs/`.

## 11. Build-docs independence

- [x] Canonical `asw` package imports successfully with `build-docs/` treated as absent.
- [x] Core tests resolve with `build-docs/` treated as absent.
- [x] Schemas resolve with `build-docs/` treated as absent.
- [x] Fixtures resolve with `build-docs/` treated as absent.
- [x] Evaluation validation resolves with `build-docs/` treated as absent.
- [x] Release/evidence tools resolve with `build-docs/` treated as absent.
- [x] Root README links resolve with `build-docs/` treated as absent.
- [x] `docs/README.md` links resolve with `build-docs/` treated as absent.
- [x] Installation succeeds without `build-docs/`.

## 12. Frozen Phase 8 evidence verification

- [x] Run ID equals `asw-mvp-eval-20260802-05`.
- [x] Base commit equals `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`.
- [x] Frozen profile digest matches the accepted run manifest.
- [x] Raw trial record count equals `736`.
- [x] Ground-truth record count equals `158`.
- [x] Agent-usage record count equals `36`.
- [x] Frozen run validation passes without modifying historical evidence.
- [x] Aggregate recomputation succeeds from frozen evidence.
- [x] Recomputed aggregate matches the accepted aggregate exactly.
- [x] Recomputed aggregate SHA-256 equals `80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C`.
- [x] Public headline metrics are derived from the accepted aggregate.
- [x] Historical Phase 8 artifacts remain unmodified after verification.

## 13. Empirical claim discipline

- [x] Live Windows claims are attributed to runtime qualification, not Phase 8 controlled evaluation.
- [x] Phase 8 is described as deterministic controlled probe timelines through the committed ASW service/reducer/agent boundary.
- [x] Phase 8 is not described as directly exercising live OS filesystem/process/UI transitions.
- [x] Runtime qualification and Phase 8 methodology are not conflated.
- [x] Layer A preregistered threshold is stated as `>=30%` reduction in at least `2 of 3` primary classes with no >2 percentage-point detection regression.
- [x] Observed Layer A result is stated separately: `3/3` classes passed and each observed `50%` reduction.
- [x] `50%` is not called the preregistered gate.
- [x] Layer B 20 ms versus 40 ms values are identified as normalized scripted protocol values.
- [x] Layer B values are not described as measured Windows execution latency.
- [x] Layer B observation-count contract is documented as one structured signal-stream read vs. two observations: notification receipt and parsing/interpretation; subscription setup and controlled event publication are excluded.
- [x] Public claims remain limited to the bounded RFC 0001 MVP proposition.
- [x] Public docs do not claim universal application support.
- [x] Public docs do not claim cross-platform validation.
- [x] Public docs do not claim universal agent benefit.
- [x] Public docs do not claim general-purpose desktop understanding.
- [x] Negative/secondary results and documented limitations remain disclosed where relevant.

## 14. Documentation-to-implementation accuracy

- [x] GUI documentation lists only controls that exist.
- [x] Applications page is not described as containing nonexistent navigation.
- [x] Event-type filtering is not presented as a GUI selector if it remains API-only.
- [x] Unscoped capability metadata is not described as requiring an active grant.
- [x] Data-bearing agent operations are described using their actual grant/authorization enforcement.
- [x] Installation commands refer to actual canonical files.
- [x] Qualified dependency filenames in documentation match files in the repository.
- [x] Documentation corrections did not require changing accepted product semantics.

## 15. Licensing

- [x] Standard MIT `LICENSE` file exists at repository root.
- [x] Project/package metadata identifies MIT consistently.
- [x] Root README references the MIT license.
- [x] No company or organization owner was invented.
- [x] Copyright/author attribution uses only the explicitly established repository owner/author identity.
- [x] Third-party dependencies are not represented as covered by the ASW MIT license.
- [x] Third-party notices are present where required.

## 16. Dependency inventory and qualification

- [x] Direct runtime dependencies are identified correctly.
- [x] Transitive runtime dependencies are identified correctly.
- [x] Development/test dependencies are identified correctly.
- [x] Release/tooling dependencies are identified correctly.
- [x] `comtypes` remains classified according to the corrected runtime dependency inventory.
- [x] `typing-extensions` remains classified according to the corrected runtime dependency inventory.
- [x] Qualified Windows/runtime dependency file exists.
- [x] Qualified development dependency file exists.
- [x] Qualified/pinned dependency files are the documented reproducibility source.
- [x] Third-party notices agree with the qualified dependency inventory.

## 17. Installation reproducibility

- [x] Installation guide states the supported Windows target.
- [x] Installation guide states the supported/qualified Python version.
- [x] Installation guide states the Windows App Runtime prerequisite.
- [x] Installation guide states every additional required Windows prerequisite, or explicitly states that none beyond the Windows App Runtime is required.
- [x] Installation guide provides the qualified dependency installation command.
- [x] Installation guide provides runtime verification steps.
- [x] Installation guide provides ASW startup instructions.
- [x] Installation does not require a sibling checkout.
- [x] Installation does not require `build-docs/`.
- [x] Installation does not require a developer Desktop path.
- [x] Installation does not rely on an undocumented environment variable or local assumption.
- [x] Clean-checkout/clean-environment smoke test was executed to the extent supported by the current machine.
- [x] Exact clean-install commands/results are recorded as release evidence.

## 18. Security and privacy

- [x] Root `SECURITY.md` exists.
- [x] `SECURITY.md` contains a concrete private reporting route.
- [x] The private reporting route is intentionally configured for this release.
- [x] Security documentation distinguishes unscoped capability metadata from grant-protected data operations.
- [x] Observation authorization is described accurately.
- [x] Agent grants/effective scope are described accurately.
- [x] Loopback API assumptions are documented.
- [x] Secret scan finds no real API keys.
- [x] Secret scan finds no private keys.
- [x] Secret scan finds no real authentication tokens.
- [x] Secret scan finds no passwords/credentials intended to remain private.
- [x] Credential-shaped fixture/test values are distinguishable from real credentials.
- [x] Packaged public text contains no workstation-specific private paths.
- [x] No release-phase security wording required expanding core behavior merely to make the prose true.

## 19. `.gitignore` and repository hygiene

- [x] Root `.gitignore` contains `/build-docs/`.
- [x] Python bytecode/cache patterns are ignored.
- [x] Test/static-analysis caches are ignored.
- [x] Local virtual environments are ignored.
- [x] Generated build/dist scratch output is ignored unless intentionally tracked.
- [x] Local logs are ignored.
- [x] Local environment/secret files are ignored.
- [x] Generated release archives are ignored where appropriate.
- [x] Canonical source is not accidentally ignored.
- [x] Canonical schemas/fixtures are not accidentally ignored.
- [x] Canonical docs are not accidentally ignored.
- [x] Qualified dependency files are not accidentally ignored.
- [x] Intended public evaluation code is not accidentally ignored.
- [x] Intended release/evidence tools are not accidentally ignored.
- [x] Final `git status` contains no unintended local construction artifacts in the release commit.

## 20. Release artifact construction

- [x] Release artifact is built from the normalized repository root.
- [x] Release artifact is not created by blindly archiving the entire working directory.
- [x] `build-docs/` is excluded.
- [x] Caches are excluded.
- [x] Bytecode is excluded.
- [x] Virtual environments are excluded.
- [x] Local logs and automation logs are excluded.
- [x] Temporary files are excluded.
- [x] Generated release archives are not recursively packaged.
- [x] Developer-only raw evidence not intended for publication is excluded.
- [x] Private machine-specific material is excluded.
- [x] Builder rejects workstation-specific absolute paths in packaged public text.
- [x] Builder rejects obvious real secret/credential material.
- [x] Release artifact includes `asw/`.
- [x] Release artifact includes intended `tests/`.
- [x] Release artifact includes `schemas/`.
- [x] Release artifact includes `fixtures/`.
- [x] Release artifact includes intended public `evaluation/` assets.
- [x] Release artifact includes required public `tools/`.
- [x] Release artifact includes canonical `docs/`.
- [x] Release artifact includes RFC 0001.
- [x] Release artifact includes canonical whitepaper/research summaries.
- [x] Release artifact includes `README.md`.
- [x] Release artifact includes `LICENSE`.
- [x] Release artifact includes `SECURITY.md`.
- [x] Release artifact includes `CHANGELOG.md`.
- [x] Release artifact includes project/package metadata.
- [x] Release artifact includes qualified dependency files.
- [x] Release artifact includes approved sanitized provenance.
- [x] Release artifact contents were inspected after construction.
- [x] Release artifact manifest/file list is recorded.
- [x] Release artifact SHA-256 is recorded.

## 21. Version consistency

- [x] Intended public release version is `v0.1.0`, unless another version was explicitly established before this pass.
- [x] Project/package metadata uses the chosen release version consistently.
- [x] Changelog uses the chosen release version consistently.
- [x] Release notes use the chosen release version consistently.
- [x] Public documentation uses the chosen version consistently where a version is stated.
- [x] Release artifact metadata uses the chosen version consistently.
- [x] No conflicting secondary version source remains.

## 22. Final validation suite

- [x] Release/package validator passes against the normalized repository.
- [x] Frozen Phase 8 evidence verifier passes.
- [x] Core unit test suite passes.
- [x] Schema/fixture validation passes.
- [x] Semantic/conformance tests pass.
- [x] Evaluation validation passes.
- [x] Compile/static validation passes.
- [x] Markdown link/path validation passes.
- [x] Canonical-document uniqueness validation passes.
- [x] Public local-path scan passes.
- [x] Secret/credential scan passes.
- [x] Dependency/pin verification passes.
- [x] Clean-install smoke passes to the extent required by this release.
- [x] Release artifact build passes.
- [x] Release artifact inspection passes.
- [x] Version consistency check passes.
- [x] `git diff --check` passes.
- [x] Final `git status` is understood and contains only intended release changes before the release commit.

## 23. Final review-agent pass

- [x] At most one final `review-agent` pass was used for this release phase.
- [x] Review packet contained the normalized tree/diff, canonical-document map, checklist state, frozen-evidence result, artifact manifest, and security/path/secret results.
- [x] Review focused only on 2–3 critical categories: release completeness/canonical paths, evidence/claim integrity, and security/privacy/package hygiene.
- [x] Material supported findings were fixed.
- [x] Affected deterministic checks were rerun after fixes.
- [x] No second review-agent loop was started.
- [x] No unresolved material review finding remains.

## 24. Hard-stop audit

Every line below MUST be false before tagging.

- [x] Phase 8 frozen evidence mismatch: **NO**.
- [x] Evaluated core semantics changed without re-evaluation: **NO**.
- [x] New reproducible core/security defect: **NO**.
- [x] Unresolved P1 release/security issue: **NO**.
- [x] Canonical promotion incomplete: **NO**.
- [x] Public operation depends on `build-docs/`: **NO**.
- [x] Public documentation links into construction workspaces: **NO**.
- [x] Workstation-specific private paths remain in packaged public files: **NO**.
- [x] Real secrets/credentials present: **NO**.
- [x] MIT license missing/inconsistent: **NO**.
- [x] Private security reporting route unusable: **NO**.
- [x] Clean installation blocked by incomplete release files/instructions: **NO**.
- [x] Public claims materially contradict accepted evidence: **NO**.
- [x] Release artifact contains excluded/private material: **NO**.
- [x] Any required checklist item above remains unchecked: **NO**.

## 25. Release decision

Choose exactly one final classification:

- [ ] `READY`
- [x] `READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS`
- [ ] `BLOCKED — RELEASE ISSUE`

Rules:

- `READY` requires every hard gate to pass with no remaining release-relevant limitation.
- `READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS` requires every hard gate to pass and every remaining limitation to be explicitly documented and noncontradictory to the bounded RFC 0001 MVP claim.
- `BLOCKED — RELEASE ISSUE` is mandatory if any hard-stop condition remains.

Final classification evidence:

```text
Classification: READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS
Rationale: All hard gates pass for the normalized ASW v0.1.0 tree; the accepted Phase 8 frozen evidence reproduces exactly, public claims are bounded, and the clean artifact operates without the construction archives.
Documented non-blocking limitations, if any: Runtime qualification is Windows 11-specific and depends on the qualified Windows App Runtime/Python environment; Phase 8 is a deterministic controlled evaluation rather than live OS-transition coverage; Layer B 20 ms versus 40 ms values are normalized scripted protocol values and its observation-count comparison is one structured signal-stream read versus two observations (notification receipt and parsing/interpretation), excluding subscription setup and controlled event publication; the bounded MVP does not claim universal application support, cross-platform validation, or general desktop understanding.
```

## 26. Release commit

Complete only if classification permits release.

- [x] All intended normalized/public files are staged intentionally.
- [x] `build-docs/` is not staged.
- [x] No raw/private/unintended artifact is staged.
- [x] Release commit was created.
- [x] Release commit SHA was recorded.

```text
Release commit SHA: recorded from the parent-root v0.1.0 tag target in the final release handoff.
```

## 27. Annotated tag

Complete only after the release commit exists and all hard gates pass.

- [x] Annotated tag name is the approved release version.
- [x] Tag message accurately describes the bounded MVP release.
- [x] Annotated tag was created.
- [x] Tag points to the intended release commit.
- [x] Tag was NOT pushed unless this task explicitly included pushing.
- [x] No hosted release was created unless this task explicitly included creating one.

```text
Tag: v0.1.0
Tag message: ASW RFC 0001 — empirically supported bounded Windows MVP
Tagged commit: recorded from the parent-root v0.1.0 tag target in the final release handoff.
```

## 28. Final release evidence report

- [x] Final report records the release classification.
- [x] Final report records the normalized repository structure.
- [x] Final report records canonical assets promoted.
- [x] Final report confirms construction workspaces moved under `build-docs/`.
- [x] Final report confirms `build-docs/` is ignored and absent from the release artifact.
- [x] Final report confirms the release operates without `build-docs/`.
- [x] Final report records release version.
- [x] Final report records release commit SHA.
- [x] Final report records tag and tag-created status.
- [x] Final report records release artifact filename and SHA-256.
- [x] Final report records frozen Phase 8 verification result and aggregate SHA-256.
- [x] Final report states whether historical Phase 8 evidence changed.
- [x] Final report records count of local-only public references removed/normalized.
- [x] Final report records provenance sanitization status.
- [x] Final report records security/secret scan result.
- [x] Final report records MIT licensing result.
- [x] Final report records dependency/clean-install result.
- [x] Final report records unit/fixture/semantic/evaluation/link validation results.
- [x] Final report records checklist completion count.
- [x] Final report records documented non-blocking limitations.
- [x] Final report records any remaining manual actions.

Final release evidence references:

- The normalized release root is the parent ASW Git repository root; no nested Git repository remains in the release tree, and the public root contains `asw/`, `tests/`, `schemas/`, `fixtures/`, `evaluation/`, `tools/`, `scripts/`, and canonical `docs/`.
- The construction workspaces are preserved under ignored `build-docs/`; the release artifact is built from the normalized root and excludes that archive, caches, bytecode, private historical evidence, and generated archives while including the accepted release-bound evidence under `evaluation/results/`.
- Frozen evidence is anchored by run `asw-mvp-eval-20260802-05`, base commit `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`, aggregate SHA-256 `80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C`, profile digest `sha256:9c38bd41057e1933cda9c54c26fa143f775d7e6bbb5cd2848423ccd7cebeb1c7`, and counts `736/158/36`; historical Phase 8 evidence was not modified.
- The final artifact filename and SHA-256, release commit SHA, and tag target are recorded in the final task handoff and the generated release manifest under ignored `release-artifacts/`.
- Security/secret scans, MIT licensing, qualified dependency checks, clean-install smoke, unit/fixture/semantic/evaluation/link validation, artifact construction, and artifact inspection all passed. No remaining manual action is required beyond any explicitly external publication decision.

---

# Definition of done

This pass is complete only when:

- [x] the repository has a conventional canonical public structure;
- [x] accepted implementation/docs/evaluation assets have been promoted without semantic reinterpretation;
- [x] construction workspaces are archived under ignored `build-docs/`;
- [x] the repository and release work with `build-docs/` absent;
- [x] public/package text contains no private workstation-only references;
- [x] immutable Phase 8 evidence reproduces exactly and remains unchanged;
- [x] empirical claims match the corrected reviewed interpretation;
- [x] licensing, security, dependencies, installation, and repository hygiene pass;
- [x] the release artifact is clean and inspected;
- [x] every required checklist item is checked;
- [x] the release classification permits tagging;
- [x] the release commit exists; and
- [x] the annotated tag exists only if every hard gate passed.
