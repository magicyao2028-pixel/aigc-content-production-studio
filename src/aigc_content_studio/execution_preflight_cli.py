from __future__ import annotations

import argparse
import json
from pathlib import Path

from .execution_preflight import build_execution_preflight, load_execution_policy


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an offline zero-send execution-scheduling preflight."
    )
    parser.add_argument("routing_plan", type=Path)
    parser.add_argument("policy", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    routing_plan = json.loads(args.routing_plan.read_text(encoding="utf-8"))
    report = build_execution_preflight(
        routing_plan, load_execution_policy(args.policy)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Execution preflight: {report['preflight_status']}; "
        "attempts: 0; external requests: 0; provider sends: 0"
    )


if __name__ == "__main__":
    main()
