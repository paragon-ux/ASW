# Troubleshooting

## The GUI does not start

Confirm that the command is run from `asw-spec-codex` and that the virtual
environment is active:

```powershell
.\.venv\Scripts\python.exe main.py
```

Then run the focused contract checks:

```powershell
.\.venv\Scripts\python.exe validate_fixtures.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

The GUI is Tk-based and needs an interactive Windows desktop session.

## Windows notifications are unavailable

The Windows App Runtime is an OS prerequisite, separate from Python packages.
Verify that Windows App Runtime `2.3.1` and the declared notification/bootstrap
packages are available to the host. ASW should keep the canonical signal even
when the sender is unavailable or a delivery attempt fails; check Activity and
the delivery audit rather than treating the missing toast as a missing signal.

## No signal appears

Check in this order:

1. The application is registered and enabled.
2. The source is registered to that application.
3. **Sources & Permissions** shows an active authorization covering the exact
   root, executable/job identity, UI Automation process, or adapter contract.
4. The event is a supported type and has sufficient reliability.
5. A filesystem artifact has completed its settle profile.
6. A degraded source has completed reconciliation.
7. The user or agent subscription matches the application/category/event type.

Widening a subscription cannot repair missing observation authorization. Avoid
using arbitrary notification text as proof that a canonical signal should
exist.

## Agent requests return 403

Confirm that:

- the token was issued by the current user grant;
- the agent subscriber ID matches the token;
- the grant is enabled and not expired;
- the subscription applications/categories are inside the grant; and
- the user authorization for those applications remains enabled.

After revocation, 403 is the expected fail-closed result for later list, read,
stream, or resume calls. Obtain a new user grant rather than reusing a revoked
token.

## A source stays degraded

The source must not return healthy merely because the watcher restarted. Check
the source health record and reconciliation result. Filesystem overflow,
unavailable roots, missed events, or reconciliation failure require a new
bounded reconciliation over the authorized scope.

## Paths or credentials appear in output

Treat local journals, tokens, and runtime logs as sensitive local data. Remove
them from release artifacts and replace examples with placeholders. Do not
publish a raw journal or a bearer token while troubleshooting.
