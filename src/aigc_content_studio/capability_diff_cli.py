from __future__ import annotations

import argparse
import json
from pathlib import Path

from .capability_diff import diff_provider_profiles
from .providers import ProviderProfile


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two provider capability profiles offline")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    baseline = ProviderProfile.from_mapping(json.loads(args.baseline.read_text(encoding="utf-8")))
    candidate = ProviderProfile.from_mapping(json.loads(args.candidate.read_text(encoding="utf-8")))
    report = diff_provider_profiles(baseline, candidate)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
