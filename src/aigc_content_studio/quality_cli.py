from __future__ import annotations

import argparse
import json
from pathlib import Path

from .quality import evaluate_quality_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a synthetic offline AIGC quality-review fixture.")
    parser.add_argument("package", type=Path, help="Production package JSON")
    parser.add_argument("taxonomy", type=Path, help="Controlled failure-taxonomy JSON")
    parser.add_argument("fixture", type=Path, help="Synthetic manually labelled review fixture")
    parser.add_argument("output", type=Path, help="Quality report JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = evaluate_quality_files(args.package, args.taxonomy, args.fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(
        f"Quality fixture evaluated: {summary['reviewed_cases']} cases, "
        f"{summary['blocked_cases']} blocked, {summary['taxonomy_coverage']:.0%} taxonomy coverage; "
        "no external call executed"
    )


if __name__ == "__main__":
    main()
