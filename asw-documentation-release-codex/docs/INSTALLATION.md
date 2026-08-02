# Installation and prerequisites

This guide installs the RFC 0001 reference MVP from the sibling
`asw-spec-codex` implementation package. It is a Windows desktop application;
the supported scope is deliberately bounded to the qualified Windows MVP.

## Tested prerequisites

- Windows 11 Pro, build `22000`, 64-bit.
- Python `3.11.9` (the accepted Phase 8 host used CPython 3.11.9).
- Windows App Runtime `2.3.1`, installed separately by the host/application
  deployment. The Python projection packages do not install this OS runtime.
- A desktop session for the Tk GUI and, for live observation, permission to
  access the explicitly authorized sources.

The optional Windows bridges use the versions declared in
[`requirements-windows.txt`](../../asw-spec-codex/requirements-windows.txt):
`watchdog`, `psutil`, `uiautomation`, `winrt-runtime`, the Windows App SDK
notification projection, and the dynamic-dependency bootstrap package.

The lower bounds in that file are the implementation contract. For a clean
reproduction of the accepted qualification, use the pinned
[`requirements-windows-qualified.txt`](../requirements-windows-qualified.txt)
and [`requirements-dev-qualified.txt`](../requirements-dev-qualified.txt)
files from this release package.

## Acquire and install from a clean checkout

The published release should be acquired from the configured repository origin
and checked out at the proposed tag:

```powershell
git clone https://github.com/paragon-ux/ASW.git ASW
Set-Location .\ASW
git checkout v0.2.0
```

If the release is supplied as an archive, extract it so the sibling
`asw-spec-codex` and `asw-documentation-release-codex` directories are present.
From the ASW workspace:

```powershell
Set-Location .\asw-spec-codex
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
.\.venv\Scripts\python.exe -m pip install -r ..\asw-documentation-release-codex\requirements-windows-qualified.txt
.\.venv\Scripts\python.exe -m pip install -r ..\asw-documentation-release-codex\requirements-dev-qualified.txt
```

The reference package does not currently declare a wheel/console-script
metadata file. Run it from the source checkout with `main.py`.

## Install and verify the Windows App Runtime

Install the Microsoft Windows App Runtime `2.3.1` host/runtime package using
the approved Microsoft deployment method for the machine; it is separate from
the Python projections. The [Microsoft Windows App SDK downloads](https://learn.microsoft.com/windows/apps/windows-app-sdk/downloads)
page is the upstream distribution reference. Verify the current-user packages
before starting ASW:

```powershell
Get-AppxPackage | Where-Object Name -match 'WindowsAppRuntime|WinAppRuntime' |
  Select-Object Name, Version, Architecture, Status
```

The accepted qualification observed the Windows App Runtime 2.3.1 components
with `Status: Ok`. If the runtime is not present or cannot bootstrap, native
notification delivery is unavailable; canonical signal history remains the
authority.

## Start the GUI

```powershell
.\.venv\Scripts\python.exe main.py
```

The launcher creates the local journal at `data\asw.journal.jsonl`, starts the
loopback agent server, starts the Windows observation runtime, and opens the
GUI. Treat the journal as local application data: it can contain paths,
application identifiers, and source metadata.

If the Windows App Runtime or an optional bridge is unavailable, ASW records a
bounded delivery/source condition rather than treating a Windows notification
as canonical signal authority. See [Troubleshooting](TROUBLESHOOTING.md).

## Verify before first use

From `asw-spec-codex`:

```powershell
.\.venv\Scripts\python.exe validate_fixtures.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

The Phase 9 package also provides a deterministic package/evidence check from
this directory:

```powershell
python validate_package.py
```

For the accepted Phase 8 run, use the commands and artifact paths in
[Evaluation reproducibility](EVALUATION_REPRODUCIBILITY.md). Do not rerun the
comparative evaluation merely to install the product.

## Uninstall and local data

Stop the GUI, remove the virtual environment if desired, and retain or delete
`asw-spec-codex\data\asw.journal.jsonl` according to local data-retention
policy. Deleting a derived index does not change semantic state, but deleting
the authoritative journal removes the local source needed for replay.
