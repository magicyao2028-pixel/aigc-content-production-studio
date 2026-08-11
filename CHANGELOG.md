# Changelog

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
