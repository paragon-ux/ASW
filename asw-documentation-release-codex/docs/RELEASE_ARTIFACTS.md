# Release artifact contents and hash procedure

The Phase 9 deliverable is currently a source tree, not a built wheel or
installer. A public source archive must be created only from a clean, reviewed
tree after the release checklist passes.

## Intended contents

Include the ASW core package, schemas, fixtures, tests, RFC, runtime evidence,
the sanitized Phase 8 manifest/aggregate/report in this package's `evidence/`
directory, and the Phase 9 public documentation set. The full evaluation
package, raw JSONL, and its source-generated report are a separate
reproducibility input and are not part of the default public archive until a
maintainer completes a separate machine-path and secret audit.

## Required exclusions

Do not include `.venv`, `__pycache__`, `.pytest_cache`, coverage/build output,
local `data` journals, credentials/tokens, editor metadata, machine-specific
logs, unsanitized evaluation reports, raw evaluation JSONL, or unreviewed
temporary evaluation runs. The root `.gitignore` records the local-output
rules.

## Audited build procedure

Run from the parent ASW workspace after reviewing the exact file list. The
release builder includes only the core and documentation roots, excludes local
output by name and directory, and fails on machine-specific paths or
credential-shaped text:

```powershell
python .\asw-documentation-release-codex\build_release_artifact.py `
  --output .\ASW-0.2.0-source.zip
```

Inspect the archive listing and compare it with the checklist before publishing
the recorded hash. Supply the separate evaluation package only through a
separately audited reproducibility distribution. The Phase 9 validation used a
transient filtered archive inspection; it did not publish or retain a release
archive in the workspace or release package.
