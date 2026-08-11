from __future__ import annotations

import argparse
import json
from pathlib import Path

from .providers import OfflineProviderAdapter, build_provider_request_plan, load_provider_profile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare offline provider request envelopes without sending them.")
    parser.add_argument("package", type=Path, help="Production package JSON")
    parser.add_argument("profile", type=Path, help="Provider profile JSON")
    parser.add_argument("output", type=Path, help="Output request-plan JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        package = json.loads(args.package.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid production package JSON: {exc.msg}") from exc
    plan = build_provider_request_plan(package, OfflineProviderAdapter(load_provider_profile(args.profile)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Offline provider request plan written to {args.output}; no request was sent")


if __name__ == "__main__":
    main()
