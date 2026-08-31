# Changelog

## 0.9.0 - 2026-08-31

- Added append-only synthetic review-history validation for human-review decisions.
- Preserved no-send, no-publication and unapplied-decision boundaries.

## 0.8.0 - 2026-08-28

- Added a deterministic human-review decision export for blocked quality and provider-capability outcomes.
- Preserved owner, blocker and next-action context while keeping approvals pending and platform writes at zero.
- Added trial and regression coverage for the non-executing decision boundary.

## 0.7.0 - 2026-08-26

- Added a versioned provider-capability diff fixture and offline comparator.
- Added breaking-change detection for removed deliverables, removed aspect ratios and reduced maximum duration.
- Extended trial evidence and CLI coverage while preserving the zero-send, synthetic-input and human-review boundaries.

## 0.6.0 - 2026-08-23

- added a deterministic offline comparison of reviewed routing-policy variants;
- reported eligibility, request count, abstract cost units, prepared-envelope count and zero external calls for each policy;
- preserved atomic blocking when a policy exceeds request or abstract-unit limits;
- added regression coverage and a machine-readable trial evidence claim for policy comparison.

## 0.5.0 - 2026-08-18

- added strict abstract cost-unit and request-quota policy validation;
- added an atomic non-sending routing preflight that emits no envelopes when a limit is exceeded;
- screened LiteLLM v1.97.0 and TokenCost 0.1.26 without forcing dependencies that add no value to the offline boundary;
- converted a clearly synthetic atomic-quota requirement into implementation and regression evidence;
- added a seven-claim evidence index, reviewer trial, deterministic report and honest real-pilot boundary.

## 0.4.0 - 2026-08-14

- added a controlled taxonomy for factual drift, identity instability, unreadable text, timing mismatch, rights risk and provider rejection;
- added a seven-case manually labelled synthetic fixture bound to sample-package asset IDs;
- added release-blocking decisions, evidence retention, ownership and severity summaries;
- added an offline quality CLI and reproducible report with zero external calls;
- added seven focused tests and explicit boundaries against claiming real generated-media quality.

## 0.3.0 - 2026-08-11

- added validated, configurable prompt-template sets for video, image and voice tasks;
- added a provider-adapter protocol and a capability-checked offline demonstration adapter;
- added a separate CLI that prepares request envelopes but never sends them;
- rejected unknown profile fields, unsafe template syntax, unsupported modalities, ratios and durations;
- added reproducible template/profile fixtures, provider-request output and eight focused tests.

## 0.2.0 - 2026-08-04

- added an explicit asset state machine with guarded review and revision paths;
- added a local JSON ledger with stable event IDs and per-asset versions;
- added initialize and transition CLI commands;
- added a reproducible asset-history example and six lifecycle regression tests;
- exposed the lifecycle and honest single-user boundary in the browser prototype and documentation.

## 0.1.0 - 2026-08-03

- added validated synthetic campaign brief;
- added strategy, short-video, cover-image and voiceover planning;
- added stable asset IDs, expected evidence and five human review gates;
- added deterministic production package, CLI, tests, documentation and static demo boundary;
- documented that no model, media generation, publishing or performance claim exists in v0.1.
