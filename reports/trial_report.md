# AIGC Studio Trial Readiness Report

> Synthetic, offline verification. No model, media, provider call or price quote is involved.

- Overall: **PASS**
- End-to-end planning and routing: PASS
- Atomic quota-block regression: PASS
- Routing-policy comparison: PASS
- Provider capability diff: PASS
- Evidence claims checked: 9
- External candidates screened: 2

## Routing-policy comparison

| Policy | Status | Requests | Abstract units | Prepared envelopes |
| --- | --- | --- | --- | --- |
| `offline-review-budget-v1@1.0` | eligible_for_human_review | 3 | 8 | 3 |
| `conservative-review-budget-v1@1.0` | blocked | 3 | 8 | 0 |
| `expanded-review-budget-v1@1.0` | eligible_for_human_review | 3 | 8 | 3 |

## Pilot boundary

- Synthetic brief and quality labels only; no real campaign, media-quality or adoption claim.
- Abstract cost units are not currency, tokens, provider pricing or a commercial quote.
- A real pilot requires approved provider terms, credentials, budgets, rights review, generated assets and accountable human approval.
