from __future__ import annotations

import argparse
import json
from pathlib import Path

from .lifecycle import ALLOWED_TRANSITIONS, AssetLedger, ledger_from_package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage a local append-only AIGC asset ledger.")
    commands = parser.add_subparsers(dest="command", required=True)

    initialize = commands.add_parser("initialize", help="Create a ledger from a production package")
    initialize.add_argument("package", type=Path)
    initialize.add_argument("ledger", type=Path)

    transition = commands.add_parser("transition", help="Record one validated asset status transition")
    transition.add_argument("ledger", type=Path)
    transition.add_argument("asset_id")
    transition.add_argument("to_status", choices=sorted(ALLOWED_TRANSITIONS))
    transition.add_argument("--actor", required=True)
    transition.add_argument("--note", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "initialize":
        ledger = ledger_from_package(args.package)
        ledger.save(args.ledger)
        print(f"Asset ledger initialized at {args.ledger}")
        return

    ledger = AssetLedger.load(args.ledger)
    event = ledger.transition(args.asset_id, args.to_status, args.actor, args.note)
    ledger.save(args.ledger)
    print(json.dumps(event, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
