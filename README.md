# ASW - Application Signals for Windows

ASW is a GUI-first Windows 11 MVP that turns explicitly user-authorized application observations into deterministic, structured signals. Subscriptions filter existing signal history; Windows notifications and the local agent endpoint are delivery/read surfaces, not signal authority.

## Release status and evidence

This repository contains the RFC 0001 MVP, released as `v0.1.0` under the MIT License. The accepted evaluated core commit is `7d6e267c6e89cdcd8a71644c67c95d2ab4260330`; the accepted Phase 8 run is `asw-mvp-eval-20260802-05`, classified `SUPPORTED`.

In the preregistered controlled Windows MVP evaluation, ASW achieved 100% transition detection with 0% duplicate and false-positive useful-signal rates. It reduced median observation effort by 50% versus the mechanically selected `ordinary_notification` baseline in all three primary scenario classes. The bounded continuation comparison retained 100% success and reduced median observation calls and continuation latency by 50%.

These results apply only to bounded controlled Windows MVP scenarios. They do not establish universal application coverage, cross-platform behavior, production-scale reliability, or universal benefit for arbitrary agents. The secondary crash/restart probe recorded ASW `subject_accuracy = 0.0` and remains a disclosed limitation.

See the [documentation index](docs/README.md), [installation guide](docs/getting-started/installation.md), [user guide](docs/guides/user-guide.md), [agent integration guide](docs/guides/agent-integration.md), [RFC 0001](docs/rfc/RFC-0001.md), [whitepaper](docs/research/WHITEPAPER.md), [evaluation results](docs/research/evaluation-results.md), and [security policy](SECURITY.md).

## How ASW works

```text
user observation authorization
        -> bounded source observations/events
        -> deterministic canonical signals
        -> user or agent subscriptions
        -> Activity, Windows delivery, or bounded agent reads
```

The reducer is finite, versioned, deterministic, and reject-by-default. Unsupported, unauthorized, invalid, hint-only, or degraded facts do not become ordinary signals. An append-only JSONL journal is authoritative; indexes and views are rebuildable projections.

## Install and start

The qualified environment is Windows 11 Pro build 22000, 64-bit, with CPython 3.11.9. Install Windows App Runtime 2.3.1 separately through the host/application deployment, then follow [Installation](docs/getting-started/installation.md):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-windows-qualified.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev-qualified.txt
.\.venv\Scripts\python.exe scripts\main.py
```

The normal user surface is the GUI. Normal agent operation uses the local structured endpoint and does not require the optional diagnostic CLI.

## Development

```powershell
python scripts\validate_fixtures.py
python -m unittest discover -s tests -q
python -m evaluation.validate
python -m unittest discover -s evaluation/tests -q
```

See [Contributing](CONTRIBUTING.md), [architecture](docs/reference/architecture.md), [reproducibility](docs/research/reproducibility.md), [known limitations](docs/reference/limitations.md), and [CHANGELOG](CHANGELOG.md). ASW is distributed under the [MIT License](LICENSE); third-party dependencies retain their own licenses as described in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
