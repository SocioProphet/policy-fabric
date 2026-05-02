#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "lattice-runtime-promotion-policy.example.json"
MANIFEST = "runtime-promotion-manifest:lattice-runtime-promotion-manifest:0.2.0"
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
REQUIRED_ACTIONS = {
    "evaluate-runtime-promotion",
    "allow-dev-runtime-promotion",
    "allow-stable-runtime-promotion",
}
TOKEN_ALIASES = {
    "RuntimeAsset-present": "RuntimeAsset",
    "SBOM-present": "SBOM",
    "scan-report-pass": "scan-report",
    "attestation-present": "attestation",
    "signature-present": "signature",
    "RuntimePromotionManifest-present": "RuntimePromotionManifest",
    "external-scanner-evidence-present": "external-scanner-evidence",
    "external-scanner-evidence-pass": "external-scanner-evidence",
    "external-signing-authority-evidence-present": "external-signing-authority-evidence",
    "external-signing-authority-evidence-verified": "external-signing-authority-evidence",
    "human-approval-present": "human-approval",
    "human-approval-approved": "human-approval",
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
        metadata = data.get("metadata")
        require(isinstance(metadata, dict), "metadata must be object")
        require(metadata.get("version") == "0.2.0", "metadata.version must be 0.2.0")
        spec = data.get("spec")
        require(isinstance(spec, dict), "spec must be object")
        require("SocioProphet/lattice-forge#13" in spec.get("trackingRefs", []), "trackingRefs must include lattice-forge#13")
        require(spec.get("runtimePromotionManifestRef") == MANIFEST, "manifest ref mismatch")
        require(set(spec.get("runtimeRefs", [])) == RUNTIME_REFS, "runtimeRefs mismatch")
        require(REQUIRED_GENERATED <= set(spec.get("requiredGeneratedEvidence", [])), "requiredGeneratedEvidence incomplete")
        require(REQUIRED_STABLE <= set(spec.get("requiredStableEvidence", [])), "requiredStableEvidence incomplete")
        require(REQUIRED_ACTIONS <= set(spec.get("actions", [])), "actions incomplete")
        require("block-stable-runtime-promotion" not in spec.get("actions", []), "stable block action must be removed after stable evidence gates exist")
        require("request-stable-runtime-review" not in spec.get("actions", []), "stable review action must be removed after stable evidence gates exist")

        gates = spec.get("promotionGates")
        require(isinstance(gates, dict), "promotionGates must be object")
        require(REQUIRED_GENERATED <= normalize(gates.get("devRuntimePromotion", [])), "devRuntimePromotion gate incomplete")
        require(REQUIRED_STABLE <= normalize(gates.get("stableRuntimePromotion", [])), "stableRuntimePromotion gate incomplete")
        stable_tokens = set(gates.get("stableRuntimePromotion", []))
        for token in ["external-scanner-evidence-pass", "external-signing-authority-evidence-verified", "human-approval-approved"]:
            require(token in stable_tokens, f"stableRuntimePromotion missing {token}")

        decisions = spec.get("decisions")
        require(isinstance(decisions, list) and len(decisions) >= 6, "decisions missing")
        dev_subjects = set()
        stable_subjects = set()
        for decision in decisions:
            require(isinstance(decision, dict), "decision must be object")
            for key in ["decisionId", "subjectRef", "subjectKind", "action", "result", "because", "evidenceRefs"]:
                require(key in decision, f"decision missing {key}")
            require(decision["subjectKind"] == "RuntimePromotionManifest", "subjectKind must be RuntimePromotionManifest")
            require(decision["action"] in REQUIRED_ACTIONS, f"unexpected action {decision['action']}")
            require(decision["result"] == "allow", "all decisions must be allow when evidence gates are satisfied")
            require(isinstance(decision["because"], list) and decision["because"], "because must be non-empty")
            require(decision["evidenceRefs"] == [MANIFEST], "evidenceRefs must point to manifest v0.2.0")
            if decision["action"] == "allow-dev-runtime-promotion":
                dev_subjects.add(decision["subjectRef"])
            if decision["action"] == "allow-stable-runtime-promotion":
                stable_subjects.add(decision["subjectRef"])
                because = "\n".join(decision["because"])
                require("external-scanner-evidence" in because, "stable decision must mention external scanner evidence")
                require("external-signing-authority-evidence" in because, "stable decision must mention external signing authority evidence")
                require("human-approval" in because, "stable decision must mention human approval")
        require(dev_subjects == RUNTIME_REFS, f"dev allow subjects mismatch: {dev_subjects}")
        require(stable_subjects == RUNTIME_REFS, f"stable allow subjects mismatch: {stable_subjects}")

        non = spec.get("nonNegotiables")
        require(isinstance(non, dict), "nonNegotiables must be object")
        require(non.get("runtimeAssetOwner") == "SocioProphet/lattice-forge", "runtimeAssetOwner mismatch")
        require(non.get("policyDecisionOwner") == "SocioProphet/policy-fabric", "policyDecisionOwner mismatch")
        require(non.get("stablePromotionDefault") == "evidence-gated", "stable promotion default mismatch")
        require(non.get("mustNotAllowStablePromotionWithGeneratedEvidenceOnly") is True, "stable generated-only bypass must be forbidden")
        require(non.get("mustRequireExternalScannerEvidence") is True, "external scanner requirement missing")
        require(non.get("mustRequireExternalSigningAuthorityEvidence") is True, "external signing authority requirement missing")
        require(non.get("mustRequireHumanApproval") is True, "human approval requirement missing")
        require(non.get("mustNotBypassPolicyFabric") is True, "policy bypass must be forbidden")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice runtime promotion policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
