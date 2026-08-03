# Business Workflow

## Current controlled flow

```mermaid
flowchart TB
    R[Business request] --> B[Structured campaign brief]
    B --> V{Facts and constraints complete?}
    V -->|No| C[Return for clarification]
    V -->|Yes| S[Content strategy]
    S --> T[Video, image and voice tasks]
    T --> M[Asset manifest]
    M --> F[Fact and claims review]
    F --> P[Brand, rights and privacy review]
    P --> A{Final human approval}
    A -->|Approved| X[External generation/editing outside v0.1]
    A -->|Rejected| C
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
