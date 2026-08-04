# Handoff

## Current state

- Release stage: v0.2 product-validation prototype.
- Maintenance completed: M1/10.
- Core flow: validated brief → strategy → video/image/voice tasks → asset manifest → explicit asset lifecycle → five human review gates.
- Execution status: planning artifacts only; no model or media generation.
- Public data: synthetic only.
- Runtime cost: zero paid API dependency.

## Verification command

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m aigc_content_studio.cli data/sample_brief.json --output output/production_package.json
PYTHONPATH=src python -m aigc_content_studio.asset_cli initialize output/production_package.json output/asset_history.json
```

## Next maintenance round

M2 should add configurable prompt templates and provider-adapter interfaces. It must preserve the current no-model default and keep provider calls outside the core workflow.

## Known limitations

- deterministic planning only;
- no model adapter or generated media;
- synthetic brief and no real campaign evidence;
- local JSON history only; no multi-user persistence, authentication, queues, cost tracking, publishing or analytics;
- browser and Python implementations are mirrored manually.
