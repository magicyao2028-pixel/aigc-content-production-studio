# Handoff

## Current state

- Release stage: v0.5 trial-readiness prototype.
- Maintenance completed: M4/10.
- Core flow: validated brief → strategy → video/image/voice tasks → prompt templates → asset manifest → atomic cost-unit/quota routing preflight → offline provider request plan → asset lifecycle → six-category quality fixture → human review gates.
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
PYTHONPATH=src python -m aigc_content_studio.routing_cli output/production_package.json data/offline_provider_profile.json data/routing_policy.json output/routing_plan.json
PYTHONPATH=src python -m aigc_content_studio.trial_cli
```

## Next maintenance round

M5 should compare alternative reviewed routing policies without inferring provider price or availability, and retain the v0.5 atomic no-send boundary.

## Known limitations

- deterministic planning only;
- no network-capable model adapter or generated media;
- synthetic quality labels only; no automated or human review of real media;
- synthetic brief and no real campaign evidence;
- local JSON history only; no multi-user persistence, authentication, live quota service, monetary cost tracking, publishing or analytics;
- browser and Python implementations are mirrored manually.
