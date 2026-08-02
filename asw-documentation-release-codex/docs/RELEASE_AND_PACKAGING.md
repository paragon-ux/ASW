# Release and packaging audit

This Phase 9 package is a source/documentation release surface. The sibling
implementation package is currently run from source; no wheel or installer
artifact is claimed unless a maintainer adds and verifies one.

## Version and license

- Proposed ASW release version: `0.2.0`.
- Proposed Git tag: `v0.2.0`.
- Release metadata source: [`PACKAGE.json`](../PACKAGE.json).
- The sibling core package metadata agrees at version `0.2.0`.
- Project license: [MIT](../LICENSE), copyright identity `paragon-ux`.
- Changelog: [`CHANGELOG.md`](../CHANGELOG.md).
- Public release notes: [`RELEASE_NOTES_0.2.0.md`](RELEASE_NOTES_0.2.0.md).

Do not create or push the tag until the final checklist is signed off.

## Runtime and development dependencies

Runtime bridge requirements are declared in
[`requirements-windows.txt`](../../asw-spec-codex/requirements-windows.txt).
The Windows App Runtime is an OS prerequisite and is not bundled by pip.
Development/conformance checks use the core package's Python standard library
test runner and schema validator. The dependency/license inventory is in
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## Inclusion and exclusion rules

Release-bound source and documentation should include:

- RFC 0001, schemas, fixtures, implementation source, tests, and the completed
  MVP/runtime evidence;
- sanitized Phase 8 profile/manifest/aggregate/report anchors; the complete
  evaluation package and raw evidence remain a separate reproducibility input
  until independently audited for publication;
- Phase 9 public guides, whitepaper, security policy, MIT license, changelog,
  release notes, claims matrix, and reproducibility instructions.

Exclude:

- virtual environments, `__pycache__`, test caches, coverage output, build
  output, editor metadata, and logs;
- local `data` directories, journals, tokens, agent credentials, and machine-
  specific runtime output;
- unsanitized evaluation reports and raw evaluation JSONL from a public
  documentation bundle. The frozen run remains reproducible when the separate
  evaluation package is supplied at the documented path.

The package `.gitignore` expresses these exclusions without ignoring the
release evidence anchors under `evidence/`.

## Clean-checkout path

From a clean Windows checkout, install and run:

```powershell
Set-Location .\asw-spec-codex
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
.\.venv\Scripts\python.exe validate_fixtures.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe main.py
```

The accepted runtime qualification, not this documentation package, is the
evidence for native Windows App SDK and live source behavior.

## Release artifact procedure

The intended file set and exclusions are documented in
[`RELEASE_ARTIFACTS.md`](RELEASE_ARTIFACTS.md). Before publishing a source
archive, run the package/link/secret/path checks, create the archive from the
reviewed tree, inspect its listing, and record a SHA-256 hash. The final tag
must point to the exact reviewed source state.
