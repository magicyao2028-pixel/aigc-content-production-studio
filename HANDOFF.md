# Handoff

## Current state

- Release stage: v0.3 product-validation prototype.
- Maintenance completed: M2/10.
- Core flow: validated brief → strategy → video/image/voice tasks → validated prompt templates → asset manifest → offline provider request plan → explicit asset lifecycle → five human review gates.
- Execution status: planning and prepared-not-sent request artifacts only; no model or media generation.
- Public data: synthetic only.
- Runtime cost: zero paid API dependency.

## Verification command

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m aigc_content_studio.cli data/sample_brief.json --templates data/prompt_templates.json --output output/production_package.json
PYTHONPATH=src python -m aigc_content_studio.provider_cli output/production_package.json data/offline_provider_profile.json output/provider_requests.json
PYTHONPATH=src python -m aigc_content_studio.asset_cli initialize output/production_package.json output/asset_history.json
```

## Next maintenance round

M3 should add a package-quality fixture and failure taxonomy covering factual drift, identity instability, unreadable text, timing mismatch, rights risk and provider rejection. Keep evaluation offline and do not claim generated-media quality without real reviewed assets.

## Known limitations

- deterministic planning only;
- no network-capable model adapter or generated media;
- synthetic brief and no real campaign evidence;
- local JSON history only; no multi-user persistence, authentication, queues, cost tracking, publishing or analytics;
- browser and Python implementations are mirrored manually.
