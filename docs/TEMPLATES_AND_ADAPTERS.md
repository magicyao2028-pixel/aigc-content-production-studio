# Prompt Templates and Provider Adapters

## Purpose

M2 separates reusable content instructions from provider-specific request preparation. A content lead can change a validated template set without editing workflow code, while a technical reviewer can inspect provider capability rules without enabling a model call.

## Template contract

Every template set has a stable ID, version and exactly three templates: `short_video`, `cover_image` and `voiceover`. Templates may use only these fields:

- `product_name`, `audience`, `aspect_ratio`, `duration_seconds`;
- `brand_voice`, `approved_facts`, `call_to_action`, `prohibited_claims`.

Each modality has mandatory placeholders. Unknown fields, attribute/index access, missing modalities, blank text and oversized templates are rejected. The final package records the template-set ID and version.

## Provider interface

`ProviderAdapter` defines one operation: convert a planned deliverable into a provider-shaped request. The included `OfflineProviderAdapter` validates:

- supported deliverable type;
- allowed aspect ratio;
- maximum duration;
- the presence of a rendered generation prompt.

The profile schema is closed. Unknown fields such as `api_key` or `endpoint` are rejected, and `external_execution_enabled: true` is forbidden in the public prototype.

## Execution boundary

The adapter creates JSON envelopes only. Every envelope reports:

```json
{
  "execution_status": "prepared_not_sent",
  "external_call_executed": false,
  "human_approval_required": true
}
```

There is no `send`, `execute`, HTTP client or provider SDK in the adapter. A future production integration requires a new reviewed implementation with secrets management, current provider terms, privacy controls, quotas, retries, cost limits and an explicit authorization gate.
