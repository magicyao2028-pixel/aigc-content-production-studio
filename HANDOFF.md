# Handoff

## Current state

- Release stage: v1.0 trial-readiness prototype.
- Maintenance completed: M9/10.
- Core flow: validated brief → strategy → video/image/voice tasks → prompt templates → asset manifest → atomic cost-unit/quota routing preflight → offline provider request plan → provider-capability diff → asset lifecycle → six-category quality fixture → human review gates.
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

## M6 result

- Added `compare_routing_policies` and three reviewed synthetic policy variants.
- The trial report now records which policies are eligible or blocked, how many envelopes would be prepared, and confirms zero external calls.
- Abstract cost units remain planning weights only; no provider price, quota service or model availability is inferred.
- Added a versioned provider-capability diff fixture that detects removed deliverables, removed aspect ratios and reduced duration before future request planning; the diff is offline, review-required and zero-send.

## M7 result

- Added a deterministic human-review decision export for blocked quality cases and breaking provider-capability changes.
- Each item retains its owner, blockers and next action; approvals remain pending and no decision execution or platform write occurs.

## M8 result

- Added append-only synthetic review-history validation for exported decisions.
- Revisions, decision references, reviewer identity and unapplied status are checked deterministically.
- History records accountability only; no decision execution or asset publication occurs.

## Next maintenance round

M10 can add bounded reviewer feedback replay, while retaining the v1.0 no-send and abstract-cost boundaries.

## M9 result

- Added feedback replay that accepts only accepted synthetic records linked to the current human-review export.
- Pending/rejected records remain excluded; duplicate IDs, unknown decisions, invalid dates and applied feedback fail closed.
- Replay is regression metadata only: no decision execution, asset publication or external call occurs.

## Known limitations

- deterministic planning only;
- no network-capable model adapter or generated media;
- synthetic quality labels only; no automated or human review of real media;
- synthetic brief and no real campaign evidence;
- local JSON history only; no multi-user persistence, authentication, live quota service, monetary cost tracking, publishing or analytics;
- browser and Python implementations are mirrored manually.
