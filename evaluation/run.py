"""Execute one frozen Phase 8 evaluation run."""

from __future__ import annotations

import argparse
from pathlib import Path

from .profile import DEFAULT_PROFILE
from .runner import EvaluationRunner


ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = ROOT / "evaluation"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output-root", type=Path, default=EVALUATION_ROOT / "results")
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--scenario-dir", type=Path, default=EVALUATION_ROOT / "scenarios")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--run-id", type=str)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_dir = EvaluationRunner(
        profile_source=args.profile, output_root=args.output_root, repo=args.repo,
        scenario_dir=args.scenario_dir, config_path=args.config, run_id=args.run_id,
    ).run()
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
