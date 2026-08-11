from __future__ import annotations

import argparse
import json
from pathlib import Path

from .brief import load_brief
from .templates import load_template_set
from .workflow import ContentProductionWorkflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an offline, reviewable multimodal production package.")
    parser.add_argument("brief", type=Path, help="Campaign brief JSON file")
    parser.add_argument("--output", type=Path, help="Optional output path for the production package")
    parser.add_argument("--templates", type=Path, help="Optional validated prompt-template JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    templates = load_template_set(args.templates) if args.templates else None
    package = ContentProductionWorkflow(templates).run(load_brief(args.brief))
    rendered = json.dumps(package, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Production package written to {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
