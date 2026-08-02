# Phase 9 — Documentation, Publication, and Release Readiness

## Purpose

Phase 9 converts the completed and empirically supported ASW RFC 0001 MVP into a publishable, understandable, reproducible repository without changing product semantics.

## Phase 9A — Evidence map and information architecture

Deliver:

- documentation inventory;
- evidence/claims matrix;
- public information architecture;
- canonical terminology audit;
- stale/duplicate/conflicting documentation cleanup plan;
- release-document set and target audiences.

Do not rewrite every document first. Establish one canonical home for each concept.

### Critical review categories

- evidence fidelity;
- claim scope;
- information architecture.

## Phase 9B — Product, integration, and operations documentation

Create/update:

- root `README.md`;
- install/prerequisites guide;
- quickstart/first-run guide;
- user guide;
- agent integration guide;
- architecture overview linked to RFC 0001;
- configuration/reference guide if configuration exists;
- troubleshooting/known limitations;
- security/privacy/authority guide;
- contributor/developer/reproducibility guide.

Public docs should explain the product in application-first language and clearly distinguish:

`observation authorization → observations/events → deterministic signals → subscriptions → delivery/read surfaces`.

### Critical review categories

- user/agent clarity;
- security/privacy accuracy;
- installation reproducibility.

## Phase 9C — Whitepaper and empirical publication

Produce a whitepaper grounded in RFC 0001 and the frozen Phase 8 evidence.

Required sections:

1. Abstract
2. Motivation and research question
3. Design principles and threat/authority model
4. System architecture
5. Deterministic signal model
6. Windows observation/delivery implementation
7. Evaluation methodology
8. Results
9. Interpretation
10. Limitations and threats to validity
11. Reproducibility
12. Related design space / positioning without unsupported comparative claims
13. Conclusion

The whitepaper MUST clearly separate:

- what the RFC specifies;
- what the implementation demonstrates;
- what runtime qualification verifies;
- what the controlled experiment empirically supports.

### Critical review categories

- methodology fidelity;
- result interpretation;
- limitation/claim discipline.

## Phase 9D — Release hygiene and pre-commit gate

Audit/fix:

- packaging metadata;
- versioning source;
- dependencies and Windows prerequisites;
- `.gitignore` / package exclude lists;
- local artifacts, journals, credentials, machine paths;
- license and third-party notices;
- security policy;
- changelog and release notes;
- repository clarity;
- clean-checkout install/test instructions;
- documentation links;
- release artifact contents;
- tag readiness.

Do not create the final tag automatically unless explicitly requested. Produce the exact proposed version/tag and commands as evidence.

### Critical review categories

- packaging/release completeness;
- licensing/security disclosure;
- public-release hygiene.

## Completion outcome

Phase 9 should finish with one of:

- `READY FOR MVP RELEASE`
- `READY WITH DOCUMENTED NON-BLOCKING LIMITATIONS`
- `BLOCKED — RELEASE ISSUE`

A release issue is something such as missing legal/license information, exposed secrets, unreproducible installation, inconsistent versioning, or a documentation-discovered contradiction that prevents truthful publication.
