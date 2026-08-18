from __future__ import annotations

import argparse
from pathlib import Path

from .trial import write_trial_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the zero-cost AIGC Studio reviewer trial.")
    parser.add_argument("--json-output", type=Path, default=Path("reports/trial_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("reports/trial_report.md"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    report = write_trial_report(root, args.json_output, args.markdown_output)
    print(f"Trial {'passed' if report['overall_passed'] else 'failed'}: {args.json_output}")


if __name__ == "__main__":
    main()
