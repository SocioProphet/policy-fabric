#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "product-suite-policy.example.json"
REQUIRED_POLICY_FAMILIES = {
    "agentLanePolicy",
    "timingTelemetryPolicy",
    "mergeReadinessPolicy",
    "sourceosCarryPolicy",
    "progressReportingPolicy",
    "serviceDeskMetricsPolicy",
    "learningLoopPolicy",
}
REQUIRED_AGENT_KINDS = {"codex", "copilot", "human"}
REQUIRED_MERGE_CHECKS = {
    "scope-compliance",
    "validation-pass",
    "evidence-present",
    "no-secrets",
    "sourceos-carry-boundary",
    "human-review",
}
REQUIRED_TIMING_FIELDS = {"taskId", "agentId", "agentKind", "workstream", "repo", "wallClockMs", "evidenceRef", "replayRef"}
REQUIRED_METRICS = {"timeToFirstActionMs", "timeToFirstPRMs", "timeToMergeMs", "turnsToCompletion", "evidenceCompletenessScore"}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")
    data = json.loads(EXAMPLE.read_text())
    if data.get("apiVersion") != "policy.socioprophet.dev/v1":
        return fail("apiVersion must be policy.socioprophet.dev/v1")
    if data.get("kind") != "ProductSuitePolicyPack":
        return fail("kind must be ProductSuitePolicyPack")
    spec = data.get("spec", {})
    missing_families = sorted(REQUIRED_POLICY_FAMILIES - set(spec))
    if missing_families:
        return fail(f"missing policy families: {missing_families}")

    lane = spec["agentLanePolicy"]
    if not all(lane.get(f"{kind}AllowedFor") or lane.get(f"{kind}RequiredFor") for kind in REQUIRED_AGENT_KINDS):
        return fail("agentLanePolicy must define codex, copilot, and human lanes")

    timing = spec["timingTelemetryPolicy"]
    timing_fields = set(timing.get("requiredFields", []))
    if REQUIRED_TIMING_FIELDS - timing_fields:
        return fail(f"timingTelemetryPolicy missing required fields: {sorted(REQUIRED_TIMING_FIELDS - timing_fields)}")
    if timing.get("sourceOfTruth") != "SocioProphet/agentplane":
        return fail("timingTelemetryPolicy.sourceOfTruth must be SocioProphet/agentplane")

    merge = spec["mergeReadinessPolicy"]
    merge_checks = set(merge.get("requiredChecks", []))
    if REQUIRED_MERGE_CHECKS - merge_checks:
        return fail(f"mergeReadinessPolicy missing checks: {sorted(REQUIRED_MERGE_CHECKS - merge_checks)}")
    if merge.get("autoMergeAllowed") is not False:
        return fail("mergeReadinessPolicy.autoMergeAllowed must be false")

    carry = spec["sourceosCarryPolicy"]
    if carry.get("role") != "carry-only":
        return fail("sourceosCarryPolicy.role must be carry-only")
    forbidden = set(carry.get("mustNot", []))
    for expected in ["promote-models", "replace-service-artifacts", "own-mutable-model-lifecycle-authority"]:
        if expected not in forbidden:
            return fail(f"sourceosCarryPolicy.mustNot missing {expected}")

    progress = spec["progressReportingPolicy"]
    if progress.get("sourceOfTruth") != "SocioProphet/sociosphere":
        return fail("progressReportingPolicy.sourceOfTruth must be SocioProphet/sociosphere")
    if progress.get("countPlanningOnlyAsComplete") is not False:
        return fail("progressReportingPolicy.countPlanningOnlyAsComplete must be false")
    if not progress.get("mustReportWorkstreams"):
        return fail("progressReportingPolicy.mustReportWorkstreams must not be empty")

    metrics = spec["serviceDeskMetricsPolicy"]
    metric_fields = set(metrics.get("requiredMetrics", []))
    if REQUIRED_METRICS - metric_fields:
        return fail(f"serviceDeskMetricsPolicy missing metrics: {sorted(REQUIRED_METRICS - metric_fields)}")
    if metrics.get("sourceOfTruth") != "SocioProphet/global-devsecops-intelligence":
        return fail("serviceDeskMetricsPolicy.sourceOfTruth must be SocioProphet/global-devsecops-intelligence")

    academy = spec["learningLoopPolicy"]
    if academy.get("sourceOfTruth") != "SocioProphet/alexandrian-academy":
        return fail("learningLoopPolicy.sourceOfTruth must be SocioProphet/alexandrian-academy")
    if academy.get("failureTaxonomyRequired") is not True:
        return fail("learningLoopPolicy.failureTaxonomyRequired must be true")

    print("OK: validated product suite policy pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
