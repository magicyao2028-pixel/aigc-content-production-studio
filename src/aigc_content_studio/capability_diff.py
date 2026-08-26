from __future__ import annotations

from typing import Any

from .providers import ProviderProfile


def diff_provider_profiles(baseline: ProviderProfile, candidate: ProviderProfile) -> dict[str, Any]:
    """Compare two validated provider profiles without contacting a provider."""
    baseline_deliverables = set(baseline.supported_deliverables)
    candidate_deliverables = set(candidate.supported_deliverables)
    baseline_ratios = set(baseline.allowed_aspect_ratios)
    candidate_ratios = set(candidate.allowed_aspect_ratios)
    removed_deliverables = sorted(baseline_deliverables - candidate_deliverables)
    added_deliverables = sorted(candidate_deliverables - baseline_deliverables)
    removed_ratios = sorted(baseline_ratios - candidate_ratios)
    added_ratios = sorted(candidate_ratios - baseline_ratios)
    duration_delta = candidate.max_duration_seconds - baseline.max_duration_seconds
    breaking_changes: list[str] = []
    if removed_deliverables:
        breaking_changes.append(f"removed deliverables: {', '.join(removed_deliverables)}")
    if removed_ratios:
        breaking_changes.append(f"removed aspect ratios: {', '.join(removed_ratios)}")
    if duration_delta < 0:
        breaking_changes.append(
            f"max duration reduced from {baseline.max_duration_seconds}s to {candidate.max_duration_seconds}s"
        )
    if candidate.external_execution_enabled:
        breaking_changes.append("candidate profile enables external execution")
    additions: list[str] = []
    if added_deliverables:
        additions.append(f"added deliverables: {', '.join(added_deliverables)}")
    if added_ratios:
        additions.append(f"added aspect ratios: {', '.join(added_ratios)}")
    if duration_delta > 0:
        additions.append(f"max duration increased by {duration_delta}s")
    status = "breaking" if breaking_changes else ("expanded" if additions else "unchanged")
    return {
        "schema_version": "1.0",
        "comparison_type": "offline provider capability diff",
        "baseline": {
            "provider_id": baseline.provider_id,
            "display_name": baseline.display_name,
        },
        "candidate": {
            "provider_id": candidate.provider_id,
            "display_name": candidate.display_name,
        },
        "status": status,
        "changes": {
            "added_deliverables": added_deliverables,
            "removed_deliverables": removed_deliverables,
            "added_aspect_ratios": added_ratios,
            "removed_aspect_ratios": removed_ratios,
            "max_duration_delta_seconds": duration_delta,
        },
        "breaking_changes": breaking_changes,
        "expansions": additions,
        "external_calls_executed": 0,
        "human_review_required": True,
        "interpretation": [
            "A breaking diff requires human review before any future provider request plan uses the candidate profile.",
            "This is a versioned fixture comparison, not a claim about live provider availability or pricing.",
            "The public adapter remains prepared-not-sent and cannot authorize external execution.",
        ],
    }
