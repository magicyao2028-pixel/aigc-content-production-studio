# Business Workflow

## Current controlled flow

```mermaid
flowchart TB
    R[Business request] --> B[Structured campaign brief]
    B --> V{Facts and constraints complete?}
    V -->|No| C[Return for clarification]
    V -->|Yes| S[Content strategy]
    S --> T[Video, image and voice tasks]
    T --> PT[Validated prompt templates]
    PT --> M[Asset manifest]
    M --> RP[Offline provider request plan]
    RP --> WAIT[Prepared, not sent]
    M --> CAND[Generated candidate recorded]
    CAND --> F[Fact and claims review]
    F --> P[Brand, rights and privacy review]
    P --> A{Final human approval}
    A -->|Approved| X[Approved final recorded]
    A -->|Changes requested| CAND
```

## Role boundaries

| Role | Responsibility |
| --- | --- |
| Business/Product Owner | Approves product facts, prohibited claims and CTA. |
| Content Operations | Owns brief quality, brand direction and production coordination. |
| AIGC Operator | Executes approved tasks in selected tools and records settings/results in a future version. |
| Reviewer | Checks product identity, rights, privacy, platform rules and final asset. |
| Authorized Publisher | Makes the final external publishing decision. |

The workflow never treats generation output as automatically approved. Rejected assets return to the task or brief that caused the problem.

The v0.3 workflow also validates prompt templates and provider capabilities before producing request envelopes. Those envelopes are planning artifacts only. The local ledger records each status change as a new event, but it does not authenticate the named actor; production approval still requires an authorized system and organizational control.
