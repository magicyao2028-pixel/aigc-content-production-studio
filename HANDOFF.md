# Handoff

## Current state

- Release stage: v0.4 product-validation prototype.
- Maintenance completed: M3/10.
- Core flow: validated brief → strategy → video/image/voice tasks → validated prompt templates → asset manifest → offline provider request plan → explicit asset lifecycle → six-category offline quality fixture → five human review gates.
- Execution status: planning and prepared-not-sent request artifacts only; no model or media generation.
- Public data: synthetic only.
- Runtime cost: zero paid API dependency.

## Verification command

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m aigc_content_studio.cli data/sample_brief.json --templates data/prompt_templates.json --output output/production_package.json
PYTHONPATH=src python -m aigc_content_studio.provider_cli output/production_package.json data/offline_provider_profile.json output/provider_requests.json
PYTHONPATH=src python -m aigc_content_studio.asset_cli initialize output/production_package.json output/asset_history.json
PYTHONPATH=src python -m aigc_content_studio.quality_cli output/production_package.json data/failure_taxonomy.json data/quality_fixture.json output/quality_report.json
```

## Next maintenance round

M4 should add a deterministic cost, quota and provider-routing policy. Keep every adapter non-sending, use explicit budget fixtures and do not infer current provider price or availability.

## Known limitations

- deterministic planning only;
- no network-capable model adapter or generated media;
- synthetic quality labels only; no automated or human review of real media;
- synthetic brief and no real campaign evidence;
- local JSON history only; no multi-user persistence, authentication, queues, cost tracking, publishing or analytics;
- browser and Python implementations are mirrored manually.
