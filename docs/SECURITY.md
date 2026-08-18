# Security and Governance

## Public prototype controls

- synthetic brief and product facts only;
- no secrets, private assets or customer information;
- no model call or external upload;
- prohibited claims are carried into task constraints and review gates;
- every deliverable and final release require human approval;
- execution status remains `planned_not_generated`.
- template placeholders are allowlisted and unsafe field access is rejected;
- provider profiles reject unknown fields and cannot enable external execution;
- provider request plans contain no credential or endpoint field and remain `prepared_not_sent`.
- routing policies use non-currency abstract units, enforce request and unit ceilings, and emit no partial envelopes when blocked;
- quality fixtures accept only `synthetic-fixture://` references and retain explicit evidence labels;
- all six controlled failure categories block fixture release and require human review.

## Risks not solved in v0.4

- prompt injection in uploaded briefs or reference files;
- storage and access control for private brand assets;
- API-key management and provider data retention;
- model-generated copyright, trademark, likeness or voice-rights violations;
- unsafe, deceptive or platform-prohibited output;
- job retries that multiply cost or publish duplicate assets;
- account takeover and unauthorized publishing.
- automated detection accuracy for factual, visual, timing or rights failures in real media.
- current provider pricing, billing, regional availability and live quota enforcement.

## Required controls before model or publishing integration

1. Store provider credentials in a secret manager, never in prompts or repositories.
2. Authenticate users and separate creator, reviewer and publisher roles.
3. Scan inputs for personal data, malicious instructions and unsupported claims.
4. Record prompts, references, model/settings, cost, candidates, approvals and final asset hashes.
5. Enforce quotas, timeouts, idempotency and a manual publishing gate.
6. Define retention, deletion, incident-response and copyright-takedown procedures.
7. Verify current provider terms and commercial rights before every integration release.

Abstract routing cost units are not prices, tokens or spend approval. Connecting this public preflight to provider execution requires a separate authenticated service, current terms review, monetary budget control and accountable approval.
