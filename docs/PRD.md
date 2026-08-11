# Product Requirements Document

## 1. Document control

| Field | Value |
| --- | --- |
| Product | AIGC Content Production Studio |
| Version | 0.3 |
| Status | Product-validation MVP |
| Primary user | Content operations lead in a small or medium-sized business |
| Public data policy | Synthetic brief and generated planning artifacts only |

## 2. Problem statement

Content teams frequently start production with an incomplete request. Product facts, prohibited claims, brand direction, deliverable specifications and approval ownership are scattered across messages. As image, video and voice tools multiply, the organization needs a controlled workflow rather than a collection of disconnected prompts.

## 3. Product hypothesis

If one validated brief produces linked multimodal tasks, stable asset IDs and mandatory review gates, a content lead can coordinate AIGC production more consistently and identify missing facts before external generation begins.

The public prototype has not been tested with real users. v0.3 validates workflow, template and request-preparation logic only.

## 4. Users and jobs to be done

### Content operations lead

- convert a business request into clear deliverables;
- preserve approved product facts and prohibited claims;
- coordinate video, image, voice and editing work;
- know which evidence is required before release;
- hand the package to internal staff or an external model/tool without losing context.

### Business owner or product owner

- verify the claims, CTA and product representation;
- see who is responsible for each review gate;
- prevent an unapproved asset from being published.

## 5. v0.3 scope

### In scope

1. Load and validate a structured campaign brief.
2. Require audience, objective, facts, constraints, voice, CTA and deliverables.
3. Build one content strategy with an explicit hypothesis.
4. Plan short-video, cover-image and voiceover tasks.
5. Assign stable asset IDs and expected evidence.
6. Attach five mandatory review gates.
7. Export a structured production package and execution trace.
8. Run offline without a paid model call.
9. Initialize a local ledger from the asset manifest.
10. Validate status changes and retain every transition event.
11. Validate configurable prompt templates against an allowlist of business fields.
12. Report the template-set identity and version in every package.
13. Validate provider capabilities and prepare reviewable request envelopes without sending them.

### Out of scope

- image, video, text or voice generation;
- model-provider authentication, network execution and production API adapters;
- asset upload, editing, binary storage or publishing;
- social account integrations and campaign analytics;
- production permissions, queues, concurrency and monitoring;
- claims of business performance or real client use.

## 6. Functional requirements

| ID | Requirement | Priority | Acceptance criterion |
| --- | --- | --- | --- |
| FR-01 | Validate brief | Must | Missing facts and unsupported deliverables fail clearly. |
| FR-02 | Build strategy | Must | Output links objective, audience, facts, voice and CTA. |
| FR-03 | Plan multimodal tasks | Must | Every requested deliverable has a stable ID, specification and quality checks. |
| FR-04 | Preserve constraints | Must | Prohibited claims appear in relevant negative constraints and review gates. |
| FR-05 | Create manifest | Must | Every task has one manifest record and expected evidence list. |
| FR-06 | Require review | Must | All deliverables and final release require human approval. |
| FR-07 | Export package | Should | CLI writes valid JSON to the requested path. |
| FR-08 | Show trace | Should | Output records the five workflow stages. |
| FR-09 | Control lifecycle | Must | Assets cannot skip from planned directly to approved final. |
| FR-10 | Preserve history | Should | Every transition adds an event and increments the asset version. |
| FR-11 | Configure prompts safely | Must | Templates define all supported modalities and reject unsafe or unknown placeholders. |
| FR-12 | Validate provider fit | Must | Unsupported type, ratio or duration fails before a request is prepared. |
| FR-13 | Prevent external execution | Must | Public profiles cannot enable sending and every request records zero execution. |

## 7. Future product metrics

- percentage of briefs accepted without clarification;
- time from request to approved production package;
- revision count caused by missing facts or inconsistent prompts;
- approval rejection rate by gate;
- asset traceability completeness;
- generation cost and failed-attempt rate after adapters exist;
- content acceptance and business outcome metrics after a controlled release.

## 8. Release gate

Do not claim reduced production time, improved content quality, saved model cost or increased conversion until a controlled pilot compares a documented baseline with reviewed outcomes.
