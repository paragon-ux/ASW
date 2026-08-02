[P1] Correct the claim that Phase 8 exercised real OS transition surfaces — docs/WHITEPAPER.md:238

The evaluation harness uses deterministic in-memory `ControlledProbe` surfaces; its UI probe has no live UI implementation, and the ASW adapter constructs a source event and passes it directly to `service.emit_event()`. Therefore, saying the controller generated transitions through normal Windows/process/filesystem/UI surfaces materially overstates the empirical methodology and conflates Phase 8 with the separate live runtime qualification.

[P2] Distinguish the observed 50% reduction from the preregistered gate — docs/CLAIMS_AND_EVIDENCE.md:20

The frozen profile sets the Layer A observation-reduction threshold to 30% and requires two primary classes to pass. The accepted run observed 50% reduction in all 3/3 classes. Calling this a “50% … gate” incorrectly strengthens the preregistered criterion; it should say that 3/3 classes passed the 30% gate and each observed a 50% reduction.

[P2] Make evidence-matrix implementation references resolvable — docs/CLAIMS_AND_EVIDENCE.md:11

Several implemented-claim rows cite paths such as `asw/reducer.py`, `asw/service.py`, and `tests/test_agent_api.py` as though they exist in the Phase 9 package. They are actually in sibling `asw-spec-codex`, while other evidence is described only as “report” or unnamed tests. This prevents the claims matrix from serving as a reliable traceability index and evades the link validator.

[P2] Reconcile the declared whitepaper canonical home with retained competing artifacts — docs/DOCUMENTATION_INFORMATION_ARCHITECTURE.md:35

The architecture says `WHITEPAPER_SPEC.md` points to the canonical whitepaper and does not compete with it, but that file does not link to `WHITEPAPER.md`. The full `templates/WHITEPAPER_DRAFT.md` is also omitted from the inventory despite duplicating substantive whitepaper claims. These artifacts need explicit noncanonical status and links, or removal from the release documentation set.

Overall assessment: Phase 9A is not ready for sign-off. Canonical terminology is otherwise consistently aligned with RFC 0001, and checked local Markdown paths and fragments resolve.

Material test gaps: `validate_package.py` passes, but it does not compare methodology prose with the evaluation harness, verify threshold wording, validate inline evidence paths, or detect unclassified duplicate canonical artifacts. No files were edited.