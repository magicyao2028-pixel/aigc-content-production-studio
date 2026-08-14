# Evaluation Plan

## Objective

Evaluate whether the workflow creates a complete, fact-constrained and reviewable production package before media generation begins.

## v0.1 deterministic checks

- required brief fields are validated;
- unsupported deliverables and invalid formats fail clearly;
- every requested deliverable receives a stable asset ID;
- video prompts contain approved facts and prohibited claims;
- every asset requires human approval;
- the package contains five mandatory review gates;
- no output claims that media has been generated.

## Current offline package-quality fixture

The v0.4 fixture contains seven synthetic manually labelled review cases bound to the sample package:

- one `pass_fixture_only` record with no labelled failure;
- six blocked records, one for each controlled category;
- retained observation, evidence, severity, accountable owner and release decision;
- zero external calls and no real-media inspection.

The fixture reports 100% taxonomy coverage because each category appears once. This is branch coverage for the evaluator, not output-quality accuracy.

Future work should expand to at least 30 independently reviewed cases covering product video, brand content, promotional content and risky-claim scenarios.

Measure:

- brief completeness detection;
- approved-fact preservation;
- prohibited-claim leakage;
- deliverable specification completeness;
- asset-manifest completeness;
- reviewer agreement by gate;
- percentage of packages requiring clarification.

## Future generated-output evaluation

Only after a model adapter exists, compare planned requirements with actual media:

- product identity consistency;
- factual and text accuracy;
- shot/action continuity;
- visual quality and platform framing;
- voice timing and rights compliance;
- rejection rate and failed-attempt cost;
- human reviewer acceptance/modification rate.

## v1.0 gate

A prompt package is not proof of media quality or business value. Production claims require approved generated assets, recorded settings, independent human review, a measured baseline and controlled outcome evidence.
