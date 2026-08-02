"""Execute one frozen Phase 8 evaluation run."""

from __future__ import annotations

import argparse
from pathlib import Path

from .profile import DEFAULT_PROFILE
from .runner import EvaluationRunner


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output-root", type=Path, default=ROOT / "evaluation" / "results")
    parser.add_argument("--repo", type=Path, default=ROOT.parent / "asw-spec-codex")
    parser.add_argument("--scenario-dir", type=Path, default=ROOT / "fixtures" / "scenarios")
    parser.add_argument("--config", type=Path, default=Path(r"C:\Users\USER\.codex\config.toml"))
    parser.add_argument("--run-id", type=str)
    args = parser.parse_args()
    run_dir = EvaluationRunner(
        profile_source=args.profile, output_root=args.output_root, repo=args.repo,
        scenario_dir=args.scenario_dir, config_path=args.config, run_id=args.run_id,
    ).run()
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

