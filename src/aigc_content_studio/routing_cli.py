from __future__ import annotations

import argparse
import json
from pathlib import Path

from .providers import OfflineProviderAdapter, load_provider_profile
from .routing import build_guarded_request_plan, load_routing_policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply an offline cost-unit and request-quota routing preflight.")
    parser.add_argument("package", type=Path)
    parser.add_argument("profile", type=Path)
    parser.add_argument("policy", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    package = json.loads(args.package.read_text(encoding="utf-8"))
    adapter = OfflineProviderAdapter(load_provider_profile(args.profile))
    report = build_guarded_request_plan(package, adapter, load_routing_policy(args.policy))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Routing preflight: {report['routing_status']}; external calls executed: 0")


if __name__ == "__main__":
    main()
