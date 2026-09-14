# Handoff

## Current state

- Release stage: v1.1 post-M10 execution-boundary-hardening prototype.
- Maintenance completed: M10/10.
- Core flow: validated brief → strategy → video/image/voice tasks → prompt templates → asset manifest → atomic cost-unit/quota routing preflight → offline provider request plan → strict zero-send execution-scheduling preflight → provider-capability diff → asset lifecycle → six-category quality fixture → human review gates.
- Execution status: planning, prepared-not-sent request artifacts and review-only job descriptors/waves; no queue, retry, provider send, model call or media generation.
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
PYTHONPATH=src python -m aigc_content_studio.execution_preflight_cli output/routing_plan.json data/execution_policy.json output/execution_preflight.json
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

## Post-M10 P2 result

- Added `execution_preflight.py` plus a strict synthetic policy with maximum concurrency, maximum attempts and a complete non-decreasing retry-backoff schedule.
- Only an eligible routing plan whose request envelopes are all `prepared_not_sent`, human-review-required and zero-call can enter the preflight.
- Canonical request fingerprints produce deterministic idempotency keys, job IDs and bounded concurrency waves for review.
- A duplicate fingerprint or request ID blocks the complete plan before any job descriptor is created. Attempts, external requests and provider sends remain zero on both passing and blocked paths.
- These are scheduling artifacts only: no queue, worker, timer, retry, model call or provider idempotency mechanism is implemented.

## Next maintenance round

Post-M10 P2 Slot 3 is complete. Do not start P3 or another maintenance wave without a separately confirmed contract; retain the no-send and abstract-cost boundaries.

## M9 result

- Added feedback replay that accepts only accepted synthetic records linked to the current human-review export.
- Pending/rejected records remain excluded; duplicate IDs, unknown decisions, invalid dates and applied feedback fail closed.
- Replay is regression metadata only: no decision execution, asset publication or external call occurs.
- M10: added stale reviewer-feedback visibility for accepted feedback older than a declared cutoff on unresolved decisions; pending/rejected items stay excluded and no reminder or decision is sent.

## Known limitations

- deterministic planning only;
- deterministic job/idempotency identifiers are local planning artifacts, not live queue records or provider guarantees;
- no network-capable model adapter or generated media;
- synthetic quality labels only; no automated or human review of real media;
- synthetic brief and no real campaign evidence;
- local JSON history only; no multi-user persistence, authentication, live quota service, durable job queue, worker, retry execution, monetary cost tracking, publishing or analytics;
- browser and Python implementations are mirrored manually.
