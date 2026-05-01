#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "lattice-data-governai-expanded-policy-subjects.example.json"

REQUIRED_SUBJECTS = {
    "ModelZooEntry",
    "ModelEndpoint",
    "PromptAsset",
    "RAGPipeline",
    "VectorIndex",
    "ResearchPackage",
    "ReviewThread",
    "ReviewDecision",
    "CitationGraph",
    "ReproductionAttempt",
    "LabelingProject",
    "AnnotationReliabilityScore",
    "TrainingDataset",
    "EvaluationDataset",
    "TrainingDatasetRecipe",
    "TrainingUsePolicy",
    "ActiveMetadataEvent",
    "TrustSignal",
    "TrustPostureSummary",
}
REQUIRED_ACTIONS = {
    "discover",
    "inspect",
    "request-access",
    "select-runtime",
    "launch-notebook",
    "run-evaluation",
    "promote-model",
    "promote-prompt",
    "publish-research-package",
    "export-artifact",
    "use-for-demo-training",
    "ingest-active-metadata",
    "consume-trust-posture",
}
REQUIRED_GATES = {
    "modelZooPromotion",
    "promptRAGPromotion",
    "researchPackagePublication",
    "annotationTrainingUse",
    "activeMetadataIngestion",
    "trustPostureConsumption",
}
REQUIRED_RESULTS = {"allow", "deny", "review-required"}
REQUIRED_TRACKING_REFS = {
    "SocioProphet/prophet-platform#300",
    "SocioProphet/prophet-platform#301",
    "SocioProphet/prophet-platform#302",
    "SocioProphet/prophet-platform#303",
    "SocioProphet/prophet-platform#304",
    "SocioProphet/prophet-platform#305",
    "SocioProphet/sherlock-search#31",
    "SocioProphet/slash-topics#24",
    "SocioProphet/new-hope#8",
}


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
        require(data.get("kind") == "LatticeDataGovernAIExpandedPolicySubjectPack", "kind must be LatticeDataGovernAIExpandedPolicySubjectPack")
        metadata = data.get("metadata")
        require(isinstance(metadata, dict), "metadata must be object")
        require(metadata.get("name") == "lattice-data-governai-expanded-policy-subjects", "metadata.name mismatch")
        spec = data.get("spec")
        require(isinstance(spec, dict), "spec must be object")

        tracking_refs = set(spec.get("trackingRefs", []))
        missing_tracking = sorted(REQUIRED_TRACKING_REFS - tracking_refs)
        require(not missing_tracking, f"missing tracking refs: {missing_tracking}")

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
        require(isinstance(decisions, list) and len(decisions) >= 6, "decisions must include at least six examples")
        result_set = set()
        subject_set = set()
        action_set = set()
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
            subject_set.add(decision["subjectKind"])
            action_set.add(decision["action"])
        missing_results = sorted(REQUIRED_RESULTS - result_set)
        require(not missing_results, f"missing decision result examples: {missing_results}")
        for subject in ["ModelZooEntry", "RAGPipeline", "TrainingDataset", "ResearchPackage", "ActiveMetadataEvent", "TrustPostureSummary"]:
            require(subject in subject_set, f"missing decision coverage for {subject}")
        for action in ["promote-model", "promote-prompt", "use-for-demo-training", "export-artifact", "ingest-active-metadata", "consume-trust-posture"]:
            require(action in action_set, f"missing action decision coverage for {action}")

        non_negotiables = spec.get("nonNegotiables")
        require(isinstance(non_negotiables, dict), "nonNegotiables must be object")
        require(non_negotiables.get("noParallelMetadataSpines") is True, "noParallelMetadataSpines must be true")
        require(non_negotiables.get("canonicalSchemaOwner") == "SourceOS-Linux/sourceos-spec", "canonicalSchemaOwner mismatch")
        require(non_negotiables.get("topicPublicSurface") == "SocioProphet/slash-topics", "topicPublicSurface mismatch")
        require(non_negotiables.get("semanticMembrane") == "SocioProphet/new-hope", "semanticMembrane mismatch")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))

    print("OK: validated expanded Lattice Data/GovernAI policy-subject pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
