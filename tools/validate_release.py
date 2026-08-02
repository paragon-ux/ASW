"""Run deterministic hard-gate checks for the normalized ASW release tree."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "asw-mvp-eval-20260802-05"
BASE_COMMIT = "7d6e267c6e89cdcd8a71644c67c95d2ab4260330"
AGGREGATE_SHA256 = "80566B8C3BBC2DD7B4E729D243A1DE09E3BD68855E62C262A5C2232FBFDA527C"
PROFILE_DIGEST = "sha256:9c38bd41057e1933cda9c54c26fa143f775d7e6bbb5cd2848423ccd7cebeb1c7"
VERSION = "0.1.0"
CLASSIFICATION_LABELS = {
    "READY",
    "READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS",
    "BLOCKED \u2014 RELEASE ISSUE",
}

REQUIRED = [
    ".gitattributes", "README.md", "LICENSE", "SECURITY.md", "CHANGELOG.md", "CONTRIBUTING.md", "PACKAGE.json", "pyproject.toml",
    "requirements-windows-qualified.txt", "requirements-dev-qualified.txt", "THIRD_PARTY_NOTICES.md",
    "asw/__init__.py", "tests/test_reducer.py", "schemas/index.json", "fixtures/valid/event.file-saved.json",
    "evaluation/__init__.py", "evaluation/schema.py", "evaluation/validate.py", "evaluation/schemas/evaluation-profile.schema.json",
    "evaluation/fixtures/valid/evaluation-profile.json", "evaluation/scenarios/job-success.json",
    "evaluation/results/asw-mvp-eval-20260802-05/agent-usage.jsonl",
    "evaluation/results/asw-mvp-eval-20260802-05/aggregate-summary.json",
    "evaluation/results/asw-mvp-eval-20260802-05/ground-truth.jsonl",
    "evaluation/results/asw-mvp-eval-20260802-05/profile.json",
    "evaluation/results/asw-mvp-eval-20260802-05/raw-results.jsonl",
    "evaluation/results/asw-mvp-eval-20260802-05/run-manifest.json",
    ".github/workflows/release-validation.yml",
    "scripts/main.py", "scripts/validate_fixtures.py",
    "tools/build_release_artifact.py", "tools/inspect_release_artifact.py", "tools/verify_frozen_evidence.py", "tools/validate_release.py",
    "docs/README.md", "docs/getting-started/installation.md", "docs/getting-started/quickstart.md",
    "docs/guides/user-guide.md", "docs/guides/agent-integration.md", "docs/guides/troubleshooting.md",
    "docs/reference/architecture.md", "docs/reference/agent-api.md", "docs/reference/signals-and-events.md",
    "docs/reference/security-and-privacy.md", "docs/reference/limitations.md", "docs/rfc/RFC-0001.md",
    "docs/research/WHITEPAPER.md", "docs/research/evaluation-methodology.md", "docs/research/evaluation-results.md",
    "docs/research/runtime-qualification.md", "docs/research/reproducibility.md",
    "docs/provenance/phase-9-mitigation-report.md", "docs/provenance/accepted-run-manifest.json",
    "docs/provenance/accepted-aggregate.json", "docs/provenance/reviews/phase-9a-review.md",
    "docs/provenance/reviews/phase-9b-review.md", "docs/provenance/reviews/phase-9c-review.md", "docs/provenance/reviews/phase-9d-review.md",
    "checklists/FINAL_RELEASE_CHECKLIST.md",
]

PUBLIC_TEXT_DIRS = (ROOT / "docs", ROOT / "evaluation" / "results")
PUBLIC_ROOT_FILES = ("README.md", "LICENSE", "SECURITY.md", "CHANGELOG.md", "CONTRIBUTING.md", "THIRD_PARTY_NOTICES.md")
MACHINE_PATH = re.compile(r"(?i)(?:[A-Z]:\\Users\\|[A-Z]:/Users/|/Users/|/home/)")
CREDENTIAL = re.compile(r"(?i)\b(?:bearer\s+[A-Za-z0-9._-]{20,}|(?:token|secret|password)\s*[:=]\s*[A-Za-z0-9+/=_-]{20,})")
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest().upper()


def public_text_files() -> list[Path]:
    files = [ROOT / name for name in PUBLIC_ROOT_FILES]
    for directory in PUBLIC_TEXT_DIRS:
        files.extend(path for path in directory.rglob("*") if path.is_file() and path.name != "ASW-Repo-Release-v0-1-0.md")
    return sorted(files)


missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
if missing:
    fail(f"missing required release files: {missing}")

package = json.loads(read("PACKAGE.json"))
metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
project = metadata["project"]
if package.get("version") != VERSION or package.get("proposed_release_version") != VERSION or package.get("proposed_tag") != "v" + VERSION:
    fail("PACKAGE.json version metadata is inconsistent")
if project.get("version") != VERSION or project.get("license", {}).get("file") != "LICENSE":
    fail("pyproject.toml version or MIT license metadata is inconsistent")
if package.get("license") != "MIT" or package.get("copyright_holder") != "paragon-ux":
    fail("PACKAGE.json license or owner metadata is inconsistent")
if package.get("accepted_core_commit") != BASE_COMMIT or package.get("accepted_evaluation_run") != RUN_ID:
    fail("accepted release anchors are inconsistent")

aggregate = json.loads(read("docs/provenance/accepted-aggregate.json"))
manifest = json.loads(read("docs/provenance/accepted-run-manifest.json"))
if sha256("docs/provenance/accepted-aggregate.json") != AGGREGATE_SHA256:
    fail("accepted aggregate SHA-256 does not match the immutable release anchor")
if aggregate.get("run_id") != RUN_ID or aggregate.get("base_commit") != BASE_COMMIT:
    fail("accepted aggregate anchors do not match")
if manifest.get("run_id") != RUN_ID or manifest.get("base_commit") != BASE_COMMIT or manifest.get("profile_digest") != PROFILE_DIGEST:
    fail("accepted run manifest anchors do not match")
audit = aggregate["threshold_audit"]
checks = {
    "classification": aggregate.get("classification") == "SUPPORTED",
    "threshold gate": audit.get("pass") is True,
    "detection": audit["correctness"]["asw_detection_success"] == 1.0,
    "duplicate rate": audit["correctness"]["asw_duplicate_rate"] == 0.0,
    "false-positive rate": audit["correctness"]["asw_false_positive_rate"] == 0.0,
    "primary classes": audit["layer_a_efficiency"]["classes_passing"] == 3,
    "Layer B observation improvement": audit["layer_b_continuation"]["observation_call_improvement"] == 0.5,
    "Layer B latency improvement": audit["layer_b_continuation"]["latency_improvement"] == 0.5,
    "Layer A model calls": audit["integrity"]["layer_a_model_calls"] == 0,
    "raw trial count": audit["integrity"]["raw_trial_records"] == 736,
    "ground-truth count": audit["integrity"]["ground_truth_records"] == 158,
    "agent-usage count": audit["integrity"]["agent_usage_records"] == 36,
}
if not all(checks.values()):
    fail(f"accepted aggregate checks failed: {[name for name, passed in checks.items() if not passed]}")

if not (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines().count("/build-docs/") == 1:
    fail(".gitignore must contain exactly one /build-docs/ rule")
attributes = read(".gitattributes")
for evidence_pattern in (
    "/evaluation/results/asw-mvp-eval-20260802-05/*.jsonl -text",
    "/evaluation/results/asw-mvp-eval-20260802-05/*.json -text",
):
    if evidence_pattern not in attributes.splitlines():
        fail(f".gitattributes does not preserve accepted evidence bytes: {evidence_pattern}")
if not read("SECURITY.md").count("mailto:work.jlines@gmail.com"):
    fail("SECURITY.md lacks the configured private reporting route")
if not read("LICENSE").startswith("MIT License") or "Copyright (c) 2026 paragon-ux" not in read("LICENSE"):
    fail("LICENSE is not the approved MIT license")
notices = read("THIRD_PARTY_NOTICES.md")
for dependency in ("comtypes", "typing-extensions", "jsonschema-specifications"):
    if dependency not in notices:
        fail(f"third-party notice is missing {dependency}")
if "typing-extensions" in read("requirements-dev-qualified.txt"):
    fail("typing-extensions is incorrectly classified as development-only")
for requirements in ("requirements-windows-qualified.txt", "requirements-dev-qualified.txt"):
    if any(line.strip() and not line.lstrip().startswith("#") and "==" not in line for line in read(requirements).splitlines()):
        fail(f"un-pinned dependency remains in {requirements}")

public_files = public_text_files()
public_text = "\n".join(path.read_text(encoding="utf-8") for path in public_files)
narrative_files = [path for path in public_files if "docs\\provenance" not in str(path)]
narrative_text = "\n".join(path.read_text(encoding="utf-8") for path in narrative_files)
required_phrases = (
    "bounded controlled Windows MVP scenarios", "ordinary_notification", "subject_accuracy = 0.0",
    "Layer A used zero model calls", RUN_ID, "MIT", "controlled deterministic transition timelines",
    "ASWService.emit_event", "ScriptedContinuationAgent", "500 ms (inclusive) to 2000 ms (exclusive)",
    "three repetitions per primary scenario", "one structured signal-stream read", "notification receipt",
    "parsing/interpretation", "Subscription setup and controlled event publication are excluded",
    "normalized scripted protocol values", "work.jlines@gmail.com",
)
for phrase in required_phrases:
    if phrase not in narrative_text:
        fail(f"public release text is missing required phrase: {phrase}")
for phrase in ("proves agents are twice as fast", "ASW halves latency in general", "ASW eliminates polling", "universally outperforms notifications"):
    if phrase.lower() in narrative_text.lower():
        fail(f"prohibited overclaim appears: {phrase}")
if "controlled real transitions" in narrative_text.lower():
    fail("public release still describes Phase 8 as controlled real transitions")
if "0.2.0" in narrative_text or "v0.2.0" in narrative_text:
    fail("obsolete 0.2.0 version remains in public release text")

for path in public_files:
    content = path.read_text(encoding="utf-8")
    if MACHINE_PATH.search(content):
        fail(f"machine-specific path appears in public file: {path.relative_to(ROOT)}")
    if CREDENTIAL.search(content):
        fail(f"credential-shaped text appears in public file: {path.relative_to(ROOT)}")
    for target in LINK.findall(content):
        target = target.strip().split("#", 1)[0].strip().strip("<>").split(" ", 1)[0]
        if not target or urlparse(target).scheme or target.startswith("//"):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            fail(f"broken relative link in {path.relative_to(ROOT)}: {target}")
        if any(part in {"build-docs", "asw-spec-codex", "asw-evaluation-extension-codex", "asw-documentation-release-codex"} for part in Path(target.replace("/", "\\")).parts):
            fail(f"public link points into a construction workspace: {path.relative_to(ROOT)} -> {target}")

for forbidden in ("docs/WHITEPAPER_SPEC.md", "docs/templates/WHITEPAPER_DRAFT.md", "docs/RELEASE_NOTES_0.2.0.md"):
    if (ROOT / forbidden).exists():
        fail(f"competing/noncanonical document remains: {forbidden}")

checklist = read("checklists/FINAL_RELEASE_CHECKLIST.md")
checkboxes = re.findall(r"^- \[([ xX])\] (.+)$", checklist, flags=re.MULTILINE)
if not checkboxes:
    fail("FINAL_RELEASE_CHECKLIST.md has no checklist items")
classification_items = [
    (value, label.strip().strip("`").strip())
    for value, label in checkboxes
    if label.strip().strip("`").strip() in CLASSIFICATION_LABELS
]
selected_classifications = [label for value, label in classification_items if value.lower() == "x"]
if len(selected_classifications) != 1:
    fail(f"FINAL_RELEASE_CHECKLIST.md must select exactly one final classification: {selected_classifications}")
if selected_classifications[0] != "READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS":
    fail(f"FINAL_RELEASE_CHECKLIST.md has an unapproved final classification: {selected_classifications[0]}")
non_classification_checkboxes = [
    value for value, label in checkboxes if label.strip().strip("`").strip() not in CLASSIFICATION_LABELS
]
if any(value.lower() != "x" for value in non_classification_checkboxes):
    fail("FINAL_RELEASE_CHECKLIST.md has unchecked hard-gate items")

print(f"OK: normalized ASW release validates ({len(REQUIRED)} required files, {len(checks)} frozen checks, {len(public_files)} public text files)")
