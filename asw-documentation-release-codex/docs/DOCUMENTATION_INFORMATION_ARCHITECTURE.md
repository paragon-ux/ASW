# Documentation information architecture

The Phase 9 release set uses one canonical home per audience and concept.
Normative semantics remain in RFC 0001 and schemas; public guides explain the
reader journey without cloning the contract.

## Reader paths

| Audience | Start here | Then use |
|---|---|---|
| New user | `README.md` | `docs/INSTALLATION.md`, `docs/QUICKSTART.md`, `docs/USER_GUIDE.md`, `docs/TROUBLESHOOTING.md` |
| Agent integrator | `docs/AGENT_INTEGRATION.md` | RFC 0001 section 18 and agent schemas |
| Maintainer/contributor | `CONTRIBUTING.md` | `docs/ARCHITECTURE_OVERVIEW.md`, `docs/EVALUATION_REPRODUCIBILITY.md` |
| Security/privacy reviewer | `SECURITY.md` | `docs/SECURITY_AND_PRIVACY.md`, RFC 0001 sections 8-9 and 16-17 |
| Research reader | `docs/WHITEPAPER.md` | `docs/CLAIMS_AND_EVIDENCE.md`, evaluation report and frozen aggregate |
| Release maintainer | `checklists/RELEASE_READINESS_CHECKLIST.md` | `docs/RELEASE_AND_PACKAGING.md`, `docs/RELEASE_ARTIFACTS.md`, release notes |

## Canonical homes

- Product definition, status, and links: root `README.md`.
- Install and first run: `docs/INSTALLATION.md` and `docs/QUICKSTART.md`.
- GUI behavior and permissions: `docs/USER_GUIDE.md`.
- Agent protocol: `docs/AGENT_INTEGRATION.md`.
- Explanatory architecture: `docs/ARCHITECTURE_OVERVIEW.md`.
- Security/privacy and local data: `docs/SECURITY_AND_PRIVACY.md` and
  `SECURITY.md`.
- Troubleshooting and known limitations: `docs/TROUBLESHOOTING.md` and
  `docs/KNOWN_LIMITATIONS.md`.
- Research/reproducibility: `docs/WHITEPAPER.md` and
  `docs/EVALUATION_REPRODUCIBILITY.md`.
- Claim scope: `docs/CLAIMS_AND_EVIDENCE.md`.
- Packaging and release artifact boundary: `docs/RELEASE_AND_PACKAGING.md`
  and `docs/RELEASE_ARTIFACTS.md`.

The older `USER_AGENT_GUIDES.md` and `SECURITY_PRIVACY.md` files remain as
requirement/index material and point to their canonical documents. The
`WHITEPAPER_SPEC.md` file is the Phase 9 writing specification, not the public
paper; the [canonical whitepaper](WHITEPAPER.md) is the release artifact. The
`templates/WHITEPAPER_DRAFT.md` file is a noncanonical drafting aid retained for
provenance; it must not be cited as evidence or treated as the published paper.
