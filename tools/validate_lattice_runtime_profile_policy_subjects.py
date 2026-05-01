#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "lattice-runtime-profile-policy-subjects.example.json"
NOTEBOOK = "runtime-asset:prophet-python-ml:0.1.0"
RAY = "runtime-asset:prophet-ray-ml:0.1.0"
BEAM = "runtime-asset:prophet-beam-dataops:0.1.0"
BINDING = "runtime-profile-binding:lattice-data-governai:0.1.0"
REQUIRED_RESULTS = {"allow", "review-required"}
REQUIRED_SUBJECT_KINDS = {
    "RuntimeAsset",
    "RuntimeProfileBinding",
    "RuntimeRoleBinding",
    "NotebookRuntimeProfile",
    "RayRuntimeProfile",
    "BeamRuntimeProfile",
}
REQUIRED_ACTIONS = {
    "discover-runtime",
    "select-runtime",
    "launch-notebook-runtime",
    "run-ray-runtime",
    "run-beam-runtime",
    "consume-runtime-profile-binding",
    "promote-runtime",
    "promote-ray-runtime",
    "promote-beam-runtime",
}
REQUIRED_GATES = {
    "notebookRuntimeLaunch",
    "rayRuntimeExecution",
    "beamRuntimeExecution",
    "runtimeProfileBindingConsumption",
}
REQUIRED_TRACKING_REFS = {
    "SocioProphet/lattice-forge#11",
    "SocioProphet/prophet-platform#306",
    "SocioProphet/agentplane#77",
    "SocioProphet/sociosphere#240",
    "SocioProphet/sherlock-search#32",
    "SocioProphet/slash-topics#25",
    "SocioProphet/new-hope#9",
}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")
    try:
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        require(data.get("apiVersion") == "policy.socioprophet.dev/v1", "apiVersion mismatch")
        require(data.get("kind") == "LatticeRuntimeProfilePolicySubjectPack", "kind mismatch")
        spec = data.get("spec")
        require(isinstance(spec, dict), "spec must be object")
        missing_tracking = sorted(REQUIRED_TRACKING_REFS - set(spec.get("trackingRefs", [])))
        require(not missing_tracking, f"missing tracking refs: {missing_tracking}")
        missing_subjects = sorted(REQUIRED_SUBJECT_KINDS - set(spec.get("subjectKinds", [])))
        require(not missing_subjects, f"missing subject kinds: {missing_subjects}")
        missing_actions = sorted(REQUIRED_ACTIONS - set(spec.get("actions", [])))
        require(not missing_actions, f"missing actions: {missing_actions}")
        gates = spec.get("promotionGates")
        require(isinstance(gates, dict), "promotionGates must be object")
        missing_gates = sorted(REQUIRED_GATES - set(gates))
        require(not missing_gates, f"missing gates: {missing_gates}")
        for gate_name, reqs in gates.items():
            require(isinstance(reqs, list) and reqs, f"{gate_name} must have non-empty requirements")
        runtime_refs = spec.get("runtimeRefs")
        require(isinstance(runtime_refs, dict), "runtimeRefs must be object")
        require(runtime_refs.get("notebookRuntimeRef") == NOTEBOOK, "notebook runtime ref mismatch")
        require(runtime_refs.get("rayRuntimeRef") == RAY, "ray runtime ref mismatch")
        require(runtime_refs.get("beamRuntimeRef") == BEAM, "beam runtime ref mismatch")
        require(runtime_refs.get("runtimeProfileBindingRef") == BINDING, "binding ref mismatch")
        decisions = spec.get("decisions")
        require(isinstance(decisions, list) and len(decisions) >= 4, "decisions must include runtime decisions")
        results = set()
        subject_refs = set()
        subject_kinds = set()
        actions = set()
        for decision in decisions:
            require(isinstance(decision, dict), "decision must be object")
            for key in ["decisionId", "subjectRef", "subjectKind", "action", "result", "because", "evidenceRefs"]:
                require(key in decision, f"decision missing {key}")
            results.add(decision["result"])
            subject_refs.add(decision["subjectRef"])
            subject_kinds.add(decision["subjectKind"])
            actions.add(decision["action"])
            require(decision["subjectKind"] in REQUIRED_SUBJECT_KINDS, "unexpected subjectKind")
            require(decision["action"] in REQUIRED_ACTIONS, "unexpected action")
            require(isinstance(decision["because"], list) and decision["because"], "because must be non-empty")
            require(isinstance(decision["evidenceRefs"], list) and decision["evidenceRefs"], "evidenceRefs must be non-empty")
        require(REQUIRED_RESULTS <= results, f"missing result coverage: {sorted(REQUIRED_RESULTS - results)}")
        require({NOTEBOOK, RAY, BEAM, BINDING} <= subject_refs, "missing subject ref decisions")
        require({"NotebookRuntimeProfile", "RayRuntimeProfile", "BeamRuntimeProfile", "RuntimeProfileBinding"} <= subject_kinds, "missing subject kind decisions")
        require({"launch-notebook-runtime", "promote-ray-runtime", "promote-beam-runtime", "consume-runtime-profile-binding"} <= actions, "missing action decisions")
        non = spec.get("nonNegotiables")
        require(isinstance(non, dict), "nonNegotiables must be object")
        require(non.get("noParallelMetadataSpines") is True, "noParallelMetadataSpines must be true")
        require(non.get("runtimeAssetOwner") == "SocioProphet/lattice-forge", "runtimeAssetOwner mismatch")
        require(non.get("runtimeProfileBindingOwner") == "SocioProphet/prophet-platform", "runtimeProfileBindingOwner mismatch")
        require(non.get("mustNotBypassPolicyFabric") is True, "mustNotBypassPolicyFabric must be true")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice runtime profile policy-subject pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
