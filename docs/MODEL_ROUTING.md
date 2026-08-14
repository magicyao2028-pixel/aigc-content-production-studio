# Model-Routing Boundary

## v0.4 behavior

The repository produces provider-neutral tasks, validates prompt templates, builds offline request envelopes and evaluates synthetic quality labels. It does not call, inspect or benchmark any model output.

| Task type | Required capability | Evidence to preserve later |
| --- | --- | --- |
| Copy/script | Fact-constrained structured text | prompt, source facts, output, reviewer edits |
| Cover image | Product-consistent image generation | reference assets, model/settings, candidates, selected final |
| Short video | Identity and action continuity in a timed sequence | references, prompt, duration, ratio, candidates, failure notes |
| Voiceover | Natural timing and licensed voice | script, voice identity/rights, settings, output, approval |

## Current adapter gate

The included profile declares supported deliverables, aspect ratios and a maximum duration. The adapter rejects incompatible tasks before creating a request envelope. Unknown fields are rejected so credentials and endpoints are not embedded in public profile files. `external_execution_enabled: true` is also rejected.

## Future routing rule

A provider adapter may be selected only after checking:

1. deliverable type, duration and aspect ratio;
2. reference-asset and identity-control needs;
3. commercial-use and voice/likeness rights;
4. regional availability and current terms;
5. cost ceiling and remaining quota;
6. privacy and data-transfer requirements;
7. fallback and human review path.

Names such as Seedance, Kling, Gemini, OpenAI or other tools may appear in future adapter examples, but availability, versions, pricing and terms are time-sensitive. They must be verified when an adapter is implemented. A tool name alone is not evidence of production capability.
