#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "model-fabric-release-promotion-policy.example.json"
REQUIRED_GATES = {
    "release-dry-run",
    "versioned-github-release",
    "immutable-artifact-url",
    "sha256",
    "sbom",
    "provenance",
    "homebrew-formula-test",
    "sourceos-carry-boundary",
}
REQUIRED_EVIDENCE = {
    "dryRunManifestRef",
    "releaseTag",
    "artifactUrl",
    "artifactSha256",
    "sbomRef",
    "provenanceRef",
    "formulaTestEvidenceRef",
    "ledgerPromotionRecordRef",
}
REQUIRED_TOOLS = {
    "model-router",
    "guardrail-fabric",
    "model-governance-ledger",
    "agent-registry",
    "prophet-cli",
    "homebrew-prophet",
}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def _require_bool(mapping: dict, key: str, expected: bool = True) -> int | None:
    if mapping.get(key) is not expected:
        return fail(f"{key} must be {str(expected).lower()}")
    return None


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")

    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    if data.get("apiVersion") != "policy.socioprophet.dev/v1":
        return fail("apiVersion must be policy.socioprophet.dev/v1")
    if data.get("kind") != "ModelFabricReleasePromotionPolicyPack":
        return fail("kind must be ModelFabricReleasePromotionPolicyPack")

    spec = data.get("spec")
    if not isinstance(spec, dict):
        return fail("spec must be an object")

    lanes = spec.get("releaseLanes", [])
    lane_names = {lane.get("name") for lane in lanes if isinstance(lane, dict)}
    for required_lane in ["development-source-formula", "stable-release-artifact-formula"]:
        if required_lane not in lane_names:
            return fail(f"missing release lane {required_lane}")

    stable_lane = next(lane for lane in lanes if lane.get("name") == "stable-release-artifact-formula")
    stable_gates = set(stable_lane.get("requiredPromotionGates", []))
    missing_gates = sorted(REQUIRED_GATES - stable_gates)
    if missing_gates:
        return fail(f"stable release lane missing gates: {missing_gates}")

    dry_run_lane = next(lane for lane in lanes if lane.get("name") == "development-source-formula")
    if dry_run_lane.get("stableReleaseReady") is not False:
        return fail("development-source-formula must not be stable release ready")
    forbidden_claims = set(dry_run_lane.get("forbiddenClaims", []))
    if "production-certification" not in forbidden_claims:
        return fail("development lane must forbid production-certification claims")

    gates = spec.get("promotionGates", {})
    for key in [
        "releaseDryRunRequiredBeforeReleaseCandidate",
        "versionedGithubReleaseRequiredBeforeStableFormula",
        "immutableArtifactUrlRequired",
        "sha256Required",
        "sbomRequired",
        "provenanceRequired",
        "homebrewFormulaTestRequired",
        "noFakeChecksumsOrPlaceholderUrlsInActiveFormulae",
        "sourceosCarryOnlyBoundaryRetained",
    ]:
        result = _require_bool(gates, key, True)
        if result is not None:
            return result

    active_formula = spec.get("activeFormulaRules", {})
    for key in ["placeholderUrlsAllowed", "placeholderSha256Allowed"]:
        result = _require_bool(active_formula, key, False)
        if result is not None:
            return result
    allowed_template_paths = set(active_formula.get("templatePlaceholdersAllowedOnlyUnder", []))
    if "Formula/templates/" not in allowed_template_paths:
        return fail("template placeholders must be restricted to Formula/templates/ or equivalent template/docs paths")

    sourceos = spec.get("sourceosBoundary", {})
    if sourceos.get("role") != "carry-only":
        return fail("sourceosBoundary.role must be carry-only")
    must_not = set(sourceos.get("mustNot", []))
    if "own-mutable-model-lifecycle-authority" not in must_not:
        return fail("sourceosBoundary must forbid mutable model lifecycle authority")

    evidence = spec.get("evidenceRequirements", {})
    missing_evidence = sorted(REQUIRED_EVIDENCE - set(evidence.get("requiredPerPromotion", [])))
    if missing_evidence:
        return fail(f"missing evidence requirements: {missing_evidence}")
    if evidence.get("readinessIsCertification") is not False:
        return fail("readinessIsCertification must be false")

    missing_tools = sorted(REQUIRED_TOOLS - set(spec.get("toolCoverage", [])))
    if missing_tools:
        return fail(f"missing tool coverage: {missing_tools}")

    print("OK: validated model-fabric release promotion policy pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
