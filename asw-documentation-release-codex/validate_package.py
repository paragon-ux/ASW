from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "EVIDENCE_BASELINE.md",
    "PHASE-9-DOCUMENTATION-AND-RELEASE.md",
    "KICKOFF_PROMPT.md",
    "PACKAGE.json",
    "LICENSE",
    "build_release_artifact.py",
    "verify_frozen_evidence.py",
    "requirements-windows-qualified.txt",
    "requirements-dev-qualified.txt",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    ".gitignore",
    "THIRD_PARTY_NOTICES.md",
    "checklists/RELEASE_READINESS_CHECKLIST.md",
    "docs/CLAIMS_AND_EVIDENCE.md",
    "docs/DOCUMENTATION_INFORMATION_ARCHITECTURE.md",
    "docs/WHITEPAPER_SPEC.md",
    "docs/WHITEPAPER.md",
    "docs/INSTALLATION.md",
    "docs/QUICKSTART.md",
    "docs/USER_GUIDE.md",
    "docs/AGENT_INTEGRATION.md",
    "docs/ARCHITECTURE_OVERVIEW.md",
    "docs/SECURITY_AND_PRIVACY.md",
    "docs/TROUBLESHOOTING.md",
    "docs/KNOWN_LIMITATIONS.md",
    "docs/EVALUATION_REPRODUCIBILITY.md",
    "docs/RELEASE_AND_PACKAGING.md",
    "docs/RELEASE_ARTIFACTS.md",
    "docs/RELEASE_NOTES_0.2.0.md",
    "templates/WHITEPAPER_DRAFT.md",
    "evidence/EVALUATION_RESULTS_2026-08-02.md",
    "evidence/aggregate-summary.json",
    "evidence/run-manifest.json",
    "evidence/RELEASE_EVIDENCE_SUMMARY.md",
    "evidence/RELEASE_RUN_MANIFEST.json",
]

PUBLIC_FILES = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "THIRD_PARTY_NOTICES.md",
    "docs",
    "checklists/RELEASE_READINESS_CHECKLIST.md",
    "evidence/EVALUATION_RESULTS_2026-08-02.md",
    "evidence/RELEASE_EVIDENCE_SUMMARY.md",
    "evidence/RELEASE_RUN_MANIFEST.json",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
if missing:
    fail(f"missing required files: {missing}")

package = json.loads(read("PACKAGE.json"))
summary = json.loads(read("evidence/aggregate-summary.json"))
manifest = json.loads(read("evidence/run-manifest.json"))
release_manifest = json.loads(read("evidence/RELEASE_RUN_MANIFEST.json"))

expected_package = {
    "version": "0.2.0",
    "license": "MIT",
    "copyright_holder": "paragon-ux",
    "proposed_release_version": "0.2.0",
    "proposed_tag": "v0.2.0",
    "accepted_core_commit": "7d6e267c6e89cdcd8a71644c67c95d2ab4260330",
    "accepted_evaluation_run": "asw-mvp-eval-20260802-05",
    "accepted_evaluation_classification": "SUPPORTED",
}
for key, value in expected_package.items():
    if package.get(key) != value:
        fail(f"PACKAGE.json {key!r} is {package.get(key)!r}, expected {value!r}")

if summary["classification"] != "SUPPORTED":
    fail("frozen aggregate is not SUPPORTED")
if summary["run_id"] != package["accepted_evaluation_run"]:
    fail("aggregate run ID does not match package metadata")
if summary["base_commit"] != package["accepted_core_commit"]:
    fail("aggregate base commit does not match package metadata")
if manifest["run_id"] != package["accepted_evaluation_run"] or manifest["base_commit"] != package["accepted_core_commit"]:
    fail("historical run manifest anchors do not match package metadata")
if release_manifest["run_id"] != package["accepted_evaluation_run"] or release_manifest["base_commit"] != package["accepted_core_commit"]:
    fail("sanitized release run manifest anchors do not match package metadata")
if release_manifest["profile_digest"] != manifest["profile_digest"]:
    fail("sanitized release run manifest changed the profile digest")

audit = summary["threshold_audit"]
checks = {
    "threshold gate": audit["pass"] is True,
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
failed_checks = [name for name, passed in checks.items() if not passed]
if failed_checks:
    fail(f"frozen evidence checks failed: {failed_checks}")

public_text = "\n".join(
    read(path) if (ROOT / path).is_file() else "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / path).rglob("*.md"))
    for path in PUBLIC_FILES
)
narrative_files = [
    "README.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md",
    "THIRD_PARTY_NOTICES.md", "docs",
]
narrative_text = "\n".join(
    read(path) if (ROOT / path).is_file() else "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / path).rglob("*.md"))
    for path in narrative_files
)
required_phrases = [
    "bounded controlled Windows MVP scenarios",
    "ordinary_notification",
    "subject_accuracy = 0.0",
    "Layer A used zero model calls",
    "asw-mvp-eval-20260802-05",
    "MIT",
    "controlled deterministic transition timelines",
    "ASWService.emit_event",
    "ScriptedContinuationAgent",
    "500 ms (inclusive) to 2000 ms (exclusive)",
    "three repetitions per primary scenario",
    "notification receipt-and-parsing",
    "work.jlines@gmail.com",
]
for phrase in required_phrases:
    if phrase not in public_text:
        fail(f"public release set is missing required phrase: {phrase}")

for phrase in ("proves agents are twice as fast", "ASW halves latency in general", "ASW eliminates polling", "universally outperforms notifications"):
    if phrase.lower() in public_text.lower():
        fail(f"prohibited overclaim appears in public release set: {phrase}")

if "controlled real transitions" in public_text.lower():
    fail("public release set still claims that Phase 8 generated real transitions")

for term in ("WEN", "Cues", "Loci", "actor-relevance"):
    if re.search(rf"\b{re.escape(term)}\b", narrative_text):
        fail(f"obsolete public terminology appears: {term}")

backslash = chr(92)
escaped_backslash = re.escape(backslash)
user_segment = "Users"
home_segment = "home"
machine_path = re.compile(
    rf"(?i)(?:[A-Z]:{escaped_backslash}{user_segment}{escaped_backslash}|[A-Z]:/{user_segment}/|/{user_segment}/|/{home_segment}/)"
)
credential = re.compile(r"(?i)\b(?:bearer\s+[A-Za-z0-9._-]{20,}|(?:token|secret|password)\s*[:=]\s*[A-Za-z0-9+/=_-]{20,})")
for path in PUBLIC_FILES:
    files = [ROOT / path] if (ROOT / path).is_file() else list((ROOT / path).rglob("*.md")) + list((ROOT / path).rglob("*.json"))
    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        if machine_path.search(content):
            fail(f"machine-specific path appears in public release file: {file_path.relative_to(ROOT)}")
        if credential.search(content):
            fail(f"credential-shaped text appears in public release file: {file_path.relative_to(ROOT)}")

link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
for path in PUBLIC_FILES:
    files = [ROOT / path] if (ROOT / path).is_file() else list((ROOT / path).rglob("*.md"))
    for file_path in files:
        for target in link_pattern.findall(file_path.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0].strip()
            if not target or urlparse(target).scheme or target.startswith("//"):
                continue
            resolved = (file_path.parent / target).resolve()
            if not resolved.exists():
                fail(f"broken relative link in {file_path.relative_to(ROOT)}: {target}")

checklist = read("checklists/RELEASE_READINESS_CHECKLIST.md")
checkboxes = re.findall(r"^- \[([ xX])\]", checklist, flags=re.MULTILINE)
if not checkboxes or any(value.lower() != "x" for value in checkboxes):
    fail("release readiness checklist is not fully signed off")
if "Final classification: READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS" not in checklist:
    fail("release readiness checklist has no approved final classification")

security = read("SECURITY.md")
if "mailto:work.jlines@gmail.com" not in security:
    fail("SECURITY.md is missing the configured private reporting mailbox")

license_text = read("LICENSE")
if not license_text.startswith("MIT License") or "Copyright (c) 2026 paragon-ux" not in license_text:
    fail("LICENSE is not the approved MIT license with the configured owner identity")

whitepaper = read("docs/WHITEPAPER.md")
for heading in (
    "## Abstract", "## 1. Motivation and research question", "## 2. Design principles",
    "## 3. Threat and authority model", "## 4. System architecture", "## 5. Deterministic signal model",
    "## 6. Windows observation and delivery", "## 7. Evaluation methodology", "## 8. Results",
    "## 9. Interpretation", "## 10. Limitations and threats to validity", "## 11. Reproducibility",
    "## 12. Related design space", "## 13. Conclusion",
):
    if heading not in whitepaper:
        fail(f"whitepaper is missing required section: {heading}")

print(f"OK: Phase 9 release package validates ({len(REQUIRED)} required files, {len(checks)} frozen evidence checks, links resolved)")
