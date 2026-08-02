# Security policy

## Reporting a vulnerability

Do not disclose credentials, local journals, machine-specific paths, or an
unfixed vulnerability in a public issue. Use the repository author's private
security mailbox, which is the configured author identity for this repository:

<mailto:work.jlines@gmail.com>

When the repository's GitHub Security Advisory feature is enabled, its private
route is also acceptable:

<https://github.com/paragon-ux/ASW/security/advisories/new>

Include the affected release/commit, a minimal reproduction, impact, and any
safe mitigation. Redact tokens and local data. Do not use a public issue for
sensitive material.

## Security boundary

ASW is local-only in RFC 0001. Users authorize observation scope, and agents
are constrained by the intersection of their requested subscription, active
user-issued grant, and user-authorized observation universe. Enforcement is
server-side. Grant or observation revocation blocks subsequent access or
ordinary observation in the affected scope; data already returned cannot be
recalled.

The append-only journal can contain local paths, application/process metadata,
UI metadata, and delivery audit records. Protect it as local sensitive data.
Windows App SDK notifications are delivery only. Replay reconstructs local
state and does not perform external side effects.

See [Security and privacy](docs/reference/security-and-privacy.md) for the full
authority, source, journal, and delivery boundaries.
