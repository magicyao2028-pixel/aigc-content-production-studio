# Offline Quality Evaluation

## Purpose

The quality layer demonstrates how a small content team can classify review failures, retain evidence and prevent release. It does not generate or inspect media.

## Controlled taxonomy

The evaluator accepts exactly six categories from [`data/failure_taxonomy.json`](../data/failure_taxonomy.json):

1. `factual_drift`;
2. `identity_instability`;
3. `unreadable_text`;
4. `timing_mismatch`;
5. `rights_risk`;
6. `provider_rejection`.

Every category has a definition, evidence requirement, accountable owner and release-blocking flag. Unknown labels fail validation instead of being silently grouped into an ambiguous “other” bucket.

## Reproducible fixture

[`data/quality_fixture.json`](../data/quality_fixture.json) contains seven manually labelled synthetic cases. Each case must:

- reference an asset ID and type from the production package;
- use a `synthetic-fixture://` candidate reference;
- retain a severity, observation and evidence note for every failure;
- require human review.

Run:

```bash
aigc-quality examples/sample_production_package.json data/failure_taxonomy.json data/quality_fixture.json output/quality_report.json
```

The checked-in [`sample quality report`](../examples/sample_quality_report.json) records seven reviewed fixture cases, six blocked cases, one `pass_fixture_only` case and 100% category coverage. These figures measure deterministic fixture coverage only.

## Evidence boundary

- No image, video or audio file is included or inspected.
- No provider response is requested.
- A `pass_fixture_only` decision means the synthetic record has no labelled failure; it is not approval of a real asset.
- Real performance requires retained candidate files, accountable reviewers, inter-reviewer checks and measured false-positive and false-negative rates.
