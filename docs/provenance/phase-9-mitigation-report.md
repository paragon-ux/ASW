All 20 review findings were resolved: 9 P1, 10 P2, and 1 P3.

## Phase 9A â€” Meitner

Review: [Phase 9A review](reviews/phase-9a-review.md)

- **[P1] Phase 8 falsely described as exercising real OS transitions**
  Resolved in [`docs/research/WHITEPAPER.md`](../research/WHITEPAPER.md) by documenting deterministic in-memory `ControlledProbe` timelines, independent ground truth, the committed `ASWService.emit_event` boundary, and separate live Windows runtime qualification.

- **[P2] 50% observation reduction confused with the 30% preregistered gate**
  Resolved in [`docs/research/claims-and-evidence.md`](../research/claims-and-evidence.md): the text now states that all 3/3 classes passed the 30% gate and each observed a 50% reduction.

- **[P2] Evidence-matrix implementation paths were not resolvable**
  Resolved by linking implementation and test references explicitly into the canonical `asw/` and `tests/` trees.

- **[P2] Competing whitepaper artifacts lacked canonical-status clarity**
  Resolved by making [`docs/research/WHITEPAPER.md`](../research/WHITEPAPER.md) the single canonical whitepaper; working specifications and templates are not part of the public documentation tree.

## Phase 9B â€” Hooke

Review: [Phase 9B review](reviews/phase-9b-review.md)

- **[P1] Documentation incorrectly claimed every agent operation required an active grant**
  Resolved in [`docs/reference/security-and-privacy.md`](../reference/security-and-privacy.md) and [`docs/guides/agent-integration.md`](../guides/agent-integration.md): capability metadata is documented as unscoped, while data-bearing operations remain grant/scope enforced; expired grants return `None`.

- **[P1] Installation was not self-contained**
  Resolved in [`docs/getting-started/installation.md`](../getting-started/installation.md) by adding clone/tag instructions, Windows App Runtime 2.3.1 acquisition and verification, explicit prerequisites, and reproducible dependency pins.

- **[P2] GUI documentation promised an event-type selector that does not exist**
  Resolved in `README.md` and `docs/guides/user-guide.md`: the GUI journey now describes applications, categories, and destinations, and notes that the GUI writes `event_types: []`; agents may use the field through the API.

- **[P2] User guide described a nonexistent Applications-page route**
  Resolved by documenting Applications as registration/listing only and identifying Sources & Permissions and Subscriptions as separate top-level pages.

- **[P2] Open-ended dependency floors prevented qualification reproduction**
  Resolved by adding `requirements-windows-qualified.txt` and `requirements-dev-qualified.txt` with validated package versions and linking them from installation documentation.

## Phase 9C â€” Popper

Review: [Phase 9C review](reviews/phase-9c-review.md)

- **[P1] Layer B values were scripted rather than independently measured runtime effects**
  Resolved in [`docs/research/WHITEPAPER.md`](../research/WHITEPAPER.md) and the evaluation guide by naming `ScriptedContinuationAgent`, documenting the assigned 1/20 ms versus 2/40 ms values, and explicitly stating that they are normalized protocol values, not measured OS execution latency.

- **[P1] Remaining â€œcontrolled real transitionsâ€ language**
  Resolved in the whitepaper abstract by replacing it with deterministic probe transition timelines and separating Phase 8 evaluation from runtime qualification.

- **[P2] Layer B repetition unit was wrong**
  Resolved by changing the methodology to three repetitions per primary scenario; with two scenarios per class, this yields six trials per condition/class.

- **[P2] Observation-count contract was undefined**
  Resolved by specifying the frozen contract exactly: ASW counts one structured signal-stream read; ordinary notification counts two observations, (1) notification receipt and (2) parsing/interpretation. Subscription setup and controlled event publication are excluded.

- **[P2] Evaluation acquisition path was not independently resolvable**
  Resolved with origin/tag checkout instructions, the canonical evaluation path, and access-restricted source-archive guidance. Later triage further added [`tools/verify_frozen_evidence.py`](../../tools/verify_frozen_evidence.py) so recomputation occurs on an isolated copy.

- **[P3] Random-delay upper bound was inaccurate**
  Resolved by documenting `[500, 2000)` / 500â€“1999 ms.

## Phase 9D â€” Kuhn

Review: [Phase 9D review](reviews/phase-9d-review.md)

- **[P1] Release checklist was entirely unsigned**
  Resolved in [`FINAL_RELEASE_CHECKLIST.md`](../../checklists/FINAL_RELEASE_CHECKLIST.md) by signing all release items, adding concrete evidence, review-pass records, and the final classification.

- **[P1] Validator accepted an incomplete checklist**
  Resolved in [`tools/validate_release.py`](../../tools/validate_release.py): it requires every checkbox to be checked, requires the approved final classification, validates the security mailbox, and audits the expanded release file set.

- **[P1] GitHub security-advisory route was unavailable**
  Resolved in [`SECURITY.md`](../../SECURITY.md) by adding the configured repository-author mailbox `work.jlines@gmail.com` as the concrete private reporting path; the GitHub advisory route remains optional when enabled.

- **[P1] Archive procedure included caches, logs, and machine-path-bearing evaluation files**
  Resolved by adding [`tools/build_release_artifact.py`](../../tools/build_release_artifact.py), which limits the public archive to canonical roots, excludes generated output and raw evaluation material, and rejects machine paths or credential-shaped text. The sanitized evidence report was also corrected and public links redirected to it.

- **[P2] Runtime transitive dependencies were misclassified**
  Resolved by classifying `comtypes` and `typing-extensions` as runtime transitive dependencies, moving `typing-extensions` into the Windows-qualified pins, removing it from the dev-only pin list, and adding `jsonschema-specifications` to the development notices.

## Final closure

The final checks passed:

- `validate_package.py`: 39 required files and 11 frozen-evidence checks.
- `verify_frozen_evidence.py`: accepted aggregate reproduced byte-for-byte.
- Aggregate SHA-256: `80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C`.
- No Phase 8 raw results, manifests, accepted aggregate, or original historical report were changed.
- No ASW core semantics were modified.
- Final release state remained `READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS`.
