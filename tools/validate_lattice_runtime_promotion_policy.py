#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "lattice-runtime-promotion-policy.example.json"
MANIFEST = "runtime-promotion-manifest:lattice-runtime-promotion-manifest:0.1.0"
RUNTIME_REFS = {
    "runtime-asset:prophet-python-ml:0.1.0",
    "runtime-asset:prophet-ray-ml:0.1.0",
    "runtime-asset:prophet-beam-dataops:0.1.0",
}
REQUIRED_GENERATED = {
    "RuntimeAsset",
    "SBOM",
    "scan-report",
    "attestation",
    "signature",
    "RuntimePromotionManifest",
}
REQUIRED_STABLE = {
    "external-scanner-evidence",
    "external-signing-authority-evidence",
    "human-approval",
}
REQUIRED_RESULTS = {"allow", "deny", "review-required"}
REQUIRED_ACTIONS = {
    "evaluate-runtime-promotion",
    "allow-dev-runtime-promotion",
    "block-stable-runtime-promotion",
    "request-stable-runtime-review",
}
TOKEN_ALIASES = {
    "RuntimeAsset-present": "RuntimeAsset",
    "SBOM-present": "SBOM",
    "scan-report-pass": "scan-report",
    "attestation-present": "attestation",
    "signature-present": "signature",
    "RuntimePromotionManifest-present": "RuntimePromotionManifest",
    "external-scanner-evidence-present": "external-scanner-evidence",
    "external-signing-authority-evidence-present": "external-signing-authority-evidence",
    "human-approval-present": "human-approval",
}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def normalize(tokens: list[str]) -> set[str]:
    return {TOKEN_ALIASES.get(token, token) for token in tokens}


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")
    try:
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        require(data.get("apiVersion") == "policy.socioprophet.dev/v1", "apiVersion mismatch")
        require(data.get("kind") == "LatticeRuntimePromotionPolicyPack", "kind mismatch")
        spec = data.get("spec")
        require(isinstance(spec, dict), "spec must be object")
        require(spec.get("runtimePromotionManifestRef") == MANIFEST, "manifest ref mismatch")
        require(set(spec.get("runtimeRefs", [])) == RUNTIME_REFS, "runtimeRefs mismatch")
        require(REQUIRED_GENERATED <= set(spec.get("requiredGeneratedEvidence", [])), "requiredGeneratedEvidence incomplete")
        require(REQUIRED_STABLE <= set(spec.get("requiredStableEvidence", [])), "requiredStableEvidence incomplete")
        require(REQUIRED_ACTIONS <= set(spec.get("actions", [])), "actions incomplete")

        gates = spec.get("promotionGates")
        require(isinstance(gates, dict), "promotionGates must be object")
        require(REQUIRED_GENERATED <= normalize(gates.get("devRuntimePromotion", [])), "devRuntimePromotion gate incomplete")
        require(REQUIRED_STABLE <= normalize(gates.get("stableRuntimePromotion", [])), "stableRuntimePromotion gate incomplete")

        decisions = spec.get("decisions")
        require(isinstance(decisions, list) and len(decisions) >= 5, "decisions missing")
        results = set()
        actions = set()
        subjects = set()
        for decision in decisions:
            require(isinstance(decision, dict), "decision must be object")
            for key in ["decisionId", "subjectRef", "subjectKind", "action", "result", "because", "evidenceRefs"]:
                require(key in decision, f"decision missing {key}")
            require(decision["subjectKind"] == "RuntimePromotionManifest", "subjectKind must be RuntimePromotionManifest")
            require(decision["action"] in REQUIRED_ACTIONS, f"unexpected action {decision['action']}")
            require(decision["result"] in REQUIRED_RESULTS, f"unexpected result {decision['result']}")
            require(isinstance(decision["because"], list) and decision["because"], "because must be non-empty")
            require(decision["evidenceRefs"] == [MANIFEST], "evidenceRefs must point to manifest")
            results.add(decision["result"])
            actions.add(decision["action"])
            subjects.add(decision["subjectRef"])
        require(REQUIRED_RESULTS <= results, f"missing result coverage: {REQUIRED_RESULTS - results}")
        require(RUNTIME_REFS <= subjects, "missing per-runtime dev allow subjects")
        require(MANIFEST in subjects, "missing manifest-level stable promotion decisions")
        require("allow-dev-runtime-promotion" in actions, "missing dev allow action")
        require("block-stable-runtime-promotion" in actions, "missing stable deny action")
        require("request-stable-runtime-review" in actions, "missing stable review action")

        non = spec.get("nonNegotiables")
        require(isinstance(non, dict), "nonNegotiables must be object")
        require(non.get("runtimeAssetOwner") == "SocioProphet/lattice-forge", "runtimeAssetOwner mismatch")
        require(non.get("policyDecisionOwner") == "SocioProphet/policy-fabric", "policyDecisionOwner mismatch")
        require(non.get("stablePromotionDefault") == "blocked", "stable promotion default mismatch")
        require(non.get("mustNotAllowStablePromotionWithGeneratedEvidenceOnly") is True, "stable generated-only bypass must be forbidden")
        require(non.get("mustNotBypassPolicyFabric") is True, "policy bypass must be forbidden")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice runtime promotion policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
