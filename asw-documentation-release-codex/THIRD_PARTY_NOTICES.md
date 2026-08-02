# Third-party dependency notices

ASW is distributed under the [MIT License](LICENSE). The following direct
Python dependencies are declared by the implementation package and were
inventoried from the installed package metadata used for Phase 9 validation.
Their own license terms remain applicable to their distributions.

| Dependency | Declared version floor | License | Source |
|---|---:|---|---|
| watchdog | 6.0 | Apache-2.0 | <https://github.com/gorakhargosh/watchdog> |
| psutil | 7.0 | BSD-3-Clause | <https://github.com/giampaolo/psutil> |
| uiautomation | 2.0 | Apache-2.0 | <https://github.com/yinkaisheng/Python-UIAutomation-for-Windows> |
| winrt-runtime | 3.2.1 | MIT | Python package metadata; Windows Runtime projection |
| winui3-Microsoft.Windows.AppNotifications | 3.2.1 | MIT | Python package metadata; Windows App SDK projection |
| wasdk-Microsoft.Windows.ApplicationModel.DynamicDependency.Bootstrap | 2.1.3 | MIT | Python package metadata; Windows App SDK bootstrap projection |

The Windows observation bridge also uses these runtime transitive packages:

- `comtypes` — MIT — <https://github.com/enthought/comtypes>
- `typing-extensions` — PSF-2.0 — <https://github.com/python/typing_extensions>

The schema-validation helper used by the conformance tooling also depends on
`jsonschema` and its transitive packages. Those packages are development/test
dependencies of the validation path rather than ASW runtime semantics:

- `jsonschema` — MIT — <https://github.com/python-jsonschema/jsonschema>
- `referencing` — MIT — <https://github.com/python-jsonschema/referencing>
- `attrs` — MIT — <https://www.attrs.org/>
- `rpds-py` — MIT — <https://github.com/crate-py/rpds>
- `jsonschema-specifications` — MIT — <https://github.com/python-jsonschema/jsonschema-specifications>

The Windows App Runtime `2.3.1` is an operating-system package installed by
the host/application deployment, not a Python dependency bundled by this
source package. Its Microsoft distribution terms remain applicable.

Before publishing a binary or vendor bundle, regenerate this inventory from
the exact lock/build environment and include any required license texts or
notices supplied by the distribution artifacts.
