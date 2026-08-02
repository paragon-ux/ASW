# Known limitations and non-goals

These limitations are part of the release boundary, not bugs to hide in
prose.

- **Windows MVP scope:** the implementation and runtime evidence are bounded to
  Windows 11 and the qualified Windows App Runtime environment. No cross-
  platform behavior is claimed.
- **Registered surfaces:** sources observe explicitly authorized roots,
  executable/job identities, UI Automation process surfaces, or explicit
  adapter contracts. ASW is not a universal application instrumentation layer.
- **Application semantics:** application and diagnostic transitions require
  explicit contracts. ASW does not infer arbitrary task success from text,
  screenshots, or a notification.
- **Settling and degradation:** filesystem hints require settling. Degraded
  sources fail closed until reconciliation succeeds, which can delay or omit
  ordinary signals while completeness is uncertain.
- **Local data sensitivity:** journals and indexes may contain paths,
  application metadata, process/job data, UI metadata, and delivery audits.
  They require ordinary local protection and are not automatically safe to
  publish.
- **Agent boundary:** access is local and user-granted. Revocation blocks future
  access but cannot recall data already returned to an agent.
- **Evaluation boundary:** the accepted result used controlled preregistered
  scenarios, a selected non-ASW baseline, and a bounded continuation agent.
  It does not establish universal agent benefit, population-level effect,
  third-party application coverage, or production-scale reliability.
- **Secondary result:** the crash/restart secondary aggregate recorded ASW
  `subject_accuracy = 0.0`. It did not invalidate the primary hard gate, but it
  materially qualifies interpretation and remains visible in the whitepaper and
  evidence report.

See [Claims and evidence](CLAIMS_AND_EVIDENCE.md) for the claim classes and
[Evaluation reproducibility](EVALUATION_REPRODUCIBILITY.md) for the frozen run
boundary.
