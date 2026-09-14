# Reviewer Trial Guide

## Purpose

This 20–25 minute offline trial shows whether a synthetic campaign brief can produce a governed multimodal package, pass an abstract cost-unit/request-quota gate, build a strict zero-send scheduling preflight, and exercise the existing six-category quality fixture. It generates no media, creates no live job or retry, sends no provider request and uses no paid service.

## Clean start

Requirements: Python 3.10 or later.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
aigc-studio-trial
```

The command writes `reports/trial_report.json` and `reports/trial_report.md`.

## Expected result

- `overall_passed` is `true`;
- the three synthetic deliverables require eight abstract cost units and are eligible only for human review;
- the quality fixture blocks six labelled failure cases and exercises all six taxonomy categories;
- a two-request quota blocks the complete plan atomically, emits zero request envelopes and executes zero external calls;
- the eligible three-request plan produces three deterministic job descriptors in two concurrency waves, all still `prepared_not_sent` with zero attempts, external requests and provider sends;
- a duplicate request fingerprint blocks atomically before job creation and leaves zero jobs and waves;
- the evidence index and external-intake records validate.

## Focused commands

```bash
aigc-studio data/sample_brief.json --templates data/prompt_templates.json --output output/production_package.json
aigc-route output/production_package.json data/offline_provider_profile.json data/routing_policy.json output/routing_plan.json
aigc-execution-preflight output/routing_plan.json data/execution_policy.json output/execution_preflight.json
aigc-quality output/production_package.json data/failure_taxonomy.json data/quality_fixture.json output/quality_report.json
python -m unittest discover -s tests -v
```

## Recovery

- If editable installation is unavailable, set `PYTHONPATH=src` and run the corresponding Python modules.
- If routing is blocked, inspect `reasons`; revise the synthetic package or reviewed policy rather than deleting the gate.
- If execution preflight is blocked, remove duplicate source requests or restore the tracked policy; do not weaken the fingerprint, strict plan-shape or zero-send checks.
- Do not interpret abstract units as provider prices. Real pricing, availability, terms and regional access must be verified at execution time.

## Real-pilot boundary

A real pilot still needs approved provider terms and credentials, an accountable monetary budget owner, rights and privacy review, an authenticated durable queue/worker, provider-supported idempotency and retry semantics, generated candidate files, human media review, durable audit storage and explicit approval before generation or publication.
