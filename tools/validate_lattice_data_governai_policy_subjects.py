#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "lattice-data-governai-policy-subjects.example.json"

REQUIRED_SUBJECTS = {
    "DataProduct",
    "DataContract",
    "RuntimeAsset",
    "NotebookSession",
    "QueryRun",
    "ModelAsset",
    "ModelZooEntry",
    "PromptAsset",
    "RAGPipeline",
    "AgentAsset",
    "EvaluationBundle",
    "Factsheet",
    "PublicationArtifact",
    "ResearchPackage",
}
REQUIRED_ACTIONS = {
    "discover",
    "request-access",
    "query",
    "launch-runtime",
    "run-notebook",
    "run-ray-job",
    "run-beam-pipeline",
    "promote-model",
    "promote-prompt",
    "publish-research-package",
    "execute-agent",
    "export-artifact",
}
REQUIRED_GATES = {
    "dataProductAccess",
    "runtimeEligibility",
    "modelPromotion",
    "publicationReview",
    "agentExecution",
}
REQUIRED_RESULTS = {"allow", "deny", "review-required"}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")
    try:
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        require(data.get("apiVersion") == "policy.socioprophet.dev/v1", "apiVersion must be policy.socioprophet.dev/v1")
        require(data.get("kind") == "LatticeDataGovernAIPolicySubjectPack", "kind must be LatticeDataGovernAIPolicySubjectPack")
        metadata = data.get("metadata")
        require(isinstance(metadata, dict), "metadata must be object")
        require(metadata.get("name") == "lattice-data-governai-policy-subjects", "metadata.name mismatch")
        spec = data.get("spec")
        require(isinstance(spec, dict), "spec must be object")

        missing_subjects = sorted(REQUIRED_SUBJECTS - set(spec.get("subjectKinds", [])))
        require(not missing_subjects, f"missing subject kinds: {missing_subjects}")
        missing_actions = sorted(REQUIRED_ACTIONS - set(spec.get("actions", [])))
        require(not missing_actions, f"missing actions: {missing_actions}")
        gates = spec.get("promotionGates")
        require(isinstance(gates, dict), "promotionGates must be object")
        missing_gates = sorted(REQUIRED_GATES - set(gates))
        require(not missing_gates, f"missing promotion gates: {missing_gates}")
        for gate_name, requirements in gates.items():
            require(isinstance(requirements, list) and requirements, f"promotionGates.{gate_name} must be non-empty list")

        decisions = spec.get("decisions")
        require(isinstance(decisions, list) and len(decisions) >= 3, "decisions must include at least three examples")
        result_set = set()
        for decision in decisions:
            require(isinstance(decision, dict), "decision entries must be objects")
            for key in ["decisionId", "subjectRef", "subjectKind", "action", "result", "because", "evidenceRefs"]:
                require(key in decision, f"decision missing {key}")
            require(decision["subjectKind"] in REQUIRED_SUBJECTS, f"unknown decision subjectKind {decision['subjectKind']}")
            require(decision["action"] in REQUIRED_ACTIONS, f"unknown decision action {decision['action']}")
            require(decision["result"] in REQUIRED_RESULTS, f"unknown decision result {decision['result']}")
            require(isinstance(decision["because"], list) and decision["because"], "decision.because must be non-empty")
            require(isinstance(decision["evidenceRefs"], list) and decision["evidenceRefs"], "decision.evidenceRefs must be non-empty")
            result_set.add(decision["result"])
        missing_results = sorted(REQUIRED_RESULTS - result_set)
        require(not missing_results, f"missing decision result examples: {missing_results}")

        non_negotiables = spec.get("nonNegotiables")
        require(isinstance(non_negotiables, dict), "nonNegotiables must be object")
        require(non_negotiables.get("noParallelMetadataSpines") is True, "noParallelMetadataSpines must be true")
        require(non_negotiables.get("canonicalSchemaOwner") == "SourceOS-Linux/sourceos-spec", "canonicalSchemaOwner mismatch")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))

    print("OK: validated Lattice Data/GovernAI policy-subject pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
