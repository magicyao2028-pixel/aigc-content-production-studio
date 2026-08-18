# Reviewer Trial Guide

## Purpose

This 20–25 minute offline trial shows whether a synthetic campaign brief can produce a governed multimodal package, pass an abstract cost-unit and request-quota preflight, and exercise the existing six-category quality fixture. It generates no media, sends no provider request and uses no paid service.

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
- the evidence index and external-intake records validate.

## Focused commands

```bash
aigc-studio data/sample_brief.json --templates data/prompt_templates.json --output output/production_package.json
aigc-route output/production_package.json data/offline_provider_profile.json data/routing_policy.json output/routing_plan.json
aigc-quality output/production_package.json data/failure_taxonomy.json data/quality_fixture.json output/quality_report.json
python -m unittest discover -s tests -v
```

## Recovery

- If editable installation is unavailable, set `PYTHONPATH=src` and run the corresponding Python modules.
- If routing is blocked, inspect `reasons`; revise the synthetic package or reviewed policy rather than deleting the gate.
- Do not interpret abstract units as provider prices. Real pricing, availability, terms and regional access must be verified at execution time.

## Real-pilot boundary

A real pilot still needs approved provider terms and credentials, an accountable monetary budget owner, rights and privacy review, generated candidate files, human media review, durable audit storage and explicit approval before generation or publication.
