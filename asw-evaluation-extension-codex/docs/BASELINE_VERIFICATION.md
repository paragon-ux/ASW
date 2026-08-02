# Accepted ASW core baseline verification

Captured before Phase 8 harness implementation:

- Core repository: `C:\Users\USER\Desktop\Frameworks\ASW\asw-spec-codex`
- Base commit: `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`
- Core-scoped worktree: clean (`git status --short -- asw-spec-codex/asw asw-spec-codex/schemas asw-spec-codex/checklists asw-spec-codex/docs` returned no paths).
- Parent worktree status: the only pre-existing status was the intentionally additive untracked sibling `asw-evaluation-extension-codex/`.
- Accepted evidence: `asw-spec-codex/checklists/MVP_COMPLETION_CHECKLIST.md` and `asw-spec-codex/docs/RUNTIME_QUALIFICATION_2026-08-02.md`.
- Instructions used: extension `AGENTS.md`, `KICKOFF_PROMPT.md`, `PHASE-8-EVALUATION.md`, and `C:\Users\USER\.codex\config.toml`.

The final run manifest repeats the commit and core-scoped status under
`baseline_verification`.
