# System Architecture

## v0.1 design goals

- one traceable brief-to-package workflow;
- no paid runtime dependency;
- provider-neutral planning artifacts;
- explicit facts, constraints, ownership and approval;
- honest separation between planning and media generation.

## Logical architecture

```mermaid
flowchart TB
    subgraph Interface
      CLI[Python CLI]
      WEB[Static browser prototype]
    end
    subgraph Workflow
      V[Brief validator]
      S[Strategy planner]
      T[Multimodal task planner]
      M[Asset manifest builder]
      G[Review-gate builder]
    end
    subgraph Artifacts
      B[Campaign brief JSON]
      P[Production package JSON]
    end
    B --> CLI --> V
    B --> WEB --> V
    V --> S --> T --> M --> G --> P
```

The browser mirrors the product flow for a zero-setup demonstration. The Python package is the reference implementation covered by automated tests.

## Component responsibilities

| Component | Responsibility |
| --- | --- |
| `brief.py` | Parse and validate the campaign brief and deliverable specifications. |
| `workflow.py` | Orchestrate strategy, multimodal tasks, manifest and review gates. |
| `cli.py` | Provide local JSON input/output. |
| `data/` | Store the synthetic public brief. |
| `examples/` | Preserve a reproducible public production package. |
| `site/` | Demonstrate the workflow without external services. |

## Future production architecture

```mermaid
flowchart LR
    U[Authenticated team] --> API[Application API]
    API --> DB[(Campaign and asset metadata)]
    API --> Q[Job queue]
    Q --> ORCH[Workflow orchestrator]
    ORCH --> IMG[Image adapter]
    ORCH --> VID[Video adapter]
    ORCH --> VOI[Voice adapter]
    ORCH --> OBJ[(Versioned asset storage)]
    ORCH --> AUDIT[(Prompts, settings, cost, reviews)]
    API --> OBS[Logs, metrics and traces]
```

Production decisions still required include authentication, roles, tenant isolation, secret storage, idempotency, queue and retry behavior, concurrency, provider quotas, cost ceilings, asset encryption, content moderation, audit logs, retention and incident response.
