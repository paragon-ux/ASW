# Installation and prerequisites

ASW is a GUI-first Windows 11 desktop MVP. Install it from a clean checkout of this normalized repository; `build-docs/` and any sibling checkout are unnecessary.

## Tested prerequisites

- Windows 11 Pro, build `22000`, 64-bit.
- CPython `3.11.9` (Python 3.11 is the qualified release line).
- Windows App Runtime `2.3.1`, installed separately by the host/application deployment. The Python projection packages do not install this OS runtime.
- An interactive desktop session for the Tk GUI and permission to access the explicitly authorized sources.

No additional Windows development or runtime prerequisite is required beyond Windows App Runtime for the qualified reference path. Optional source/delivery bridges remain bounded by the authorization and host capabilities.

The qualified Python pins are the reproducibility source:

```powershell
python -m pip install -r requirements-windows-qualified.txt
python -m pip install -r requirements-dev-qualified.txt
```

The Windows-qualified set includes the runtime bridge packages and the runtime-transitive `comtypes` and `typing-extensions` pins. The development set contains the JSON Schema validation dependencies. See [third-party notices](../../THIRD_PARTY_NOTICES.md).

## Acquire and install from a clean checkout

Acquire the repository from its configured public origin and select the release tag:

```powershell
git clone https://github.com/paragon-ux/ASW.git ASW
Set-Location .\ASW
git checkout v0.1.0
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-windows-qualified.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev-qualified.txt
```

The package is runnable directly from the checkout. No wheel or console-script installation is required for the reference MVP.

## Install and verify the Windows App Runtime

Install Microsoft Windows App Runtime `2.3.1` using the approved Microsoft deployment method for the machine; it is separate from the Python projections. The [Microsoft Windows App SDK downloads](https://learn.microsoft.com/windows/apps/windows-app-sdk/downloads) page is the upstream distribution reference. Verify the current-user packages before starting ASW:

```powershell
Get-AppxPackage | Where-Object Name -match 'WindowsAppRuntime|WinAppRuntime' |
  Select-Object Name, Version, Architecture, Status
```

The accepted qualification observed the Windows App Runtime 2.3.1 components with `Status: Ok`. If the runtime is unavailable, native notification delivery may be unavailable; canonical signal history remains the authority.

## Start the GUI

```powershell
.\.venv\Scripts\python.exe main.py
```

The launcher creates local application data under `data\`, starts the loopback agent server, starts available Windows observation bridges, and opens the GUI. Treat the journal as local sensitive data: it can contain paths, application identifiers, and source metadata.

## Verify before first use

From the repository root:

```powershell
.\.venv\Scripts\python.exe validate_fixtures.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m evaluation.validate
.\.venv\Scripts\python.exe -m unittest discover -s evaluation/tests -q
```

For release validation, run `python tools\validate_release.py`. For the accepted historical evaluation, follow [Evaluation reproducibility](../research/reproducibility.md); do not rerun the comparative experiment merely to install the product.

## Uninstall and local data

Stop the GUI, remove `.venv` if desired, and retain or delete `data\asw.journal.jsonl` according to local data-retention policy. Deleting a derived index does not change semantic state; deleting the authoritative journal removes the local source needed for replay.
