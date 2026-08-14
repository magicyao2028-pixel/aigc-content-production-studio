from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


FAILURE_CATEGORIES = (
    "factual_drift",
    "identity_instability",
    "unreadable_text",
    "timing_mismatch",
    "rights_risk",
    "provider_rejection",
)
SEVERITIES = {"low", "medium", "high", "critical"}


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid {label} JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def evaluate_quality_fixture(
    package: dict[str, Any],
    taxonomy: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate manually labelled offline review records; no media or provider is invoked."""
    taxonomy_by_category = _validate_taxonomy(taxonomy)
    assets = _package_assets(package)
    cases = fixture.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Quality fixture cases must be a non-empty list")
    if fixture.get("fixture_type") != "synthetic_manually_labelled_reviews":
        raise ValueError("Quality fixture must declare synthetic_manually_labelled_reviews")

    results: list[dict[str, Any]] = []
    case_ids: set[str] = set()
    failure_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each quality case must be an object")
        case_id = _required_text(case, "case_id")
        if case_id in case_ids:
            raise ValueError("Quality case IDs must be unique")
        case_ids.add(case_id)
        asset_id = _required_text(case, "asset_id")
        if asset_id not in assets:
            raise ValueError(f"Unknown quality fixture asset ID: {asset_id}")
        asset_type = _required_text(case, "asset_type")
        if asset_type != assets[asset_id]:
            raise ValueError(f"Asset type mismatch for {asset_id}")
        candidate_reference = _required_text(case, "candidate_reference")
        if not candidate_reference.startswith("synthetic-fixture://"):
            raise ValueError("candidate_reference must use the synthetic-fixture:// scheme")

        failures = case.get("failures")
        if not isinstance(failures, list):
            raise ValueError(f"{case_id} failures must be a list")
        seen_categories: set[str] = set()
        normalized_failures: list[dict[str, Any]] = []
        release_blocked = False
        for failure in failures:
            if not isinstance(failure, dict):
                raise ValueError(f"{case_id} failures must contain objects")
            category = _required_text(failure, "category")
            if category not in taxonomy_by_category:
                raise ValueError(f"Unknown failure category: {category}")
            if category in seen_categories:
                raise ValueError(f"Duplicate failure category in {case_id}: {category}")
            seen_categories.add(category)
            severity = _required_text(failure, "severity")
            if severity not in SEVERITIES:
                raise ValueError(f"Unsupported severity: {severity}")
            evidence = _required_text(failure, "evidence")
            observation = _required_text(failure, "observation")
            release_blocking = bool(taxonomy_by_category[category]["release_blocking"])
            release_blocked = release_blocked or release_blocking
            failure_counts[category] += 1
            severity_counts[severity] += 1
            normalized_failures.append(
                {
                    "category": category,
                    "severity": severity,
                    "evidence": evidence,
                    "observation": observation,
                    "owner": taxonomy_by_category[category]["owner"],
                    "release_blocking": release_blocking,
                }
            )

        results.append(
            {
                "case_id": case_id,
                "asset_id": asset_id,
                "asset_type": asset_type,
                "candidate_reference": candidate_reference,
                "failure_count": len(normalized_failures),
                "failures": normalized_failures,
                "release_decision": "blocked" if release_blocked else "pass_fixture_only",
                "human_review_required": True,
            }
        )

    blocked = sum(item["release_decision"] == "blocked" for item in results)
    categories_exercised = sorted(failure_counts)
    return {
        "report_version": "1.0",
        "campaign_id": str(package.get("campaign_id", "")),
        "fixture_type": fixture["fixture_type"],
        "summary": {
            "reviewed_cases": len(results),
            "blocked_cases": blocked,
            "pass_fixture_only_cases": len(results) - blocked,
            "taxonomy_categories": len(FAILURE_CATEGORIES),
            "categories_exercised": len(categories_exercised),
            "taxonomy_coverage": round(len(categories_exercised) / len(FAILURE_CATEGORIES), 4),
            "failure_counts": {category: failure_counts[category] for category in FAILURE_CATEGORIES},
            "severity_counts": {severity: severity_counts[severity] for severity in sorted(SEVERITIES)},
        },
        "cases": results,
        "external_calls_executed": 0,
        "release_boundary": "Pass means only that a synthetic review record contains no labelled failure; it is not media-quality approval.",
        "evidence_boundary": [
            "The fixture is synthetic and manually labelled.",
            "No image, video, audio or provider response was generated or inspected by this evaluator.",
            "Real quality claims require reviewed candidate files, accountable reviewers and retained evidence.",
        ],
    }


def evaluate_quality_files(
    package_path: Path,
    taxonomy_path: Path,
    fixture_path: Path,
) -> dict[str, Any]:
    return evaluate_quality_fixture(
        load_json_object(package_path, "production package"),
        load_json_object(taxonomy_path, "failure taxonomy"),
        load_json_object(fixture_path, "quality fixture"),
    )


def _validate_taxonomy(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    categories = taxonomy.get("categories")
    if not isinstance(categories, list):
        raise ValueError("Failure taxonomy categories must be a list")
    by_category: dict[str, dict[str, Any]] = {}
    for item in categories:
        if not isinstance(item, dict):
            raise ValueError("Failure taxonomy entries must be objects")
        category = _required_text(item, "category")
        if category in by_category:
            raise ValueError(f"Duplicate taxonomy category: {category}")
        _required_text(item, "definition")
        _required_text(item, "evidence_required")
        _required_text(item, "owner")
        if not isinstance(item.get("release_blocking"), bool):
            raise ValueError(f"release_blocking must be boolean for {category}")
        by_category[category] = item
    if set(by_category) != set(FAILURE_CATEGORIES):
        missing = sorted(set(FAILURE_CATEGORIES).difference(by_category))
        extra = sorted(set(by_category).difference(FAILURE_CATEGORIES))
        raise ValueError(f"Taxonomy must define the six controlled categories; missing={missing}, extra={extra}")
    return by_category


def _package_assets(package: dict[str, Any]) -> dict[str, str]:
    manifest = package.get("asset_manifest")
    if not isinstance(manifest, list) or not manifest:
        raise ValueError("Production package asset_manifest must be a non-empty list")
    assets: dict[str, str] = {}
    for item in manifest:
        if not isinstance(item, dict):
            raise ValueError("Asset manifest entries must be objects")
        asset_id = _required_text(item, "asset_id")
        asset_type = _required_text(item, "type")
        if asset_id in assets:
            raise ValueError("Asset manifest IDs must be unique")
        assets[asset_id] = asset_type
    return assets


def _required_text(value: dict[str, Any], field: str) -> str:
    text = str(value.get(field, "")).strip()
    if not text:
        raise ValueError(f"{field} must not be blank")
    return text
