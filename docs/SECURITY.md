# Security and Governance

## Public prototype controls

- synthetic brief and product facts only;
- no secrets, private assets or customer information;
- no model call or external upload;
- prohibited claims are carried into task constraints and review gates;
- every deliverable and final release require human approval;
- execution status remains `planned_not_generated`.

## Risks not solved in v0.1

- prompt injection in uploaded briefs or reference files;
- storage and access control for private brand assets;
- API-key management and provider data retention;
- model-generated copyright, trademark, likeness or voice-rights violations;
- unsafe, deceptive or platform-prohibited output;
- job retries that multiply cost or publish duplicate assets;
- account takeover and unauthorized publishing.

## Required controls before model or publishing integration

1. Store provider credentials in a secret manager, never in prompts or repositories.
2. Authenticate users and separate creator, reviewer and publisher roles.
3. Scan inputs for personal data, malicious instructions and unsupported claims.
4. Record prompts, references, model/settings, cost, candidates, approvals and final asset hashes.
5. Enforce quotas, timeouts, idempotency and a manual publishing gate.
6. Define retention, deletion, incident-response and copyright-takedown procedures.
7. Verify current provider terms and commercial rights before every integration release.
