#!/usr/bin/env python3
"""Validate Policy Fabric's Semantic Enterprise v0.1 policy-input fixture."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/semantic-enterprise/v0.1/policy-input.example.json"

REQUIRED_SECTORS = {"finance", "threat-intel", "investigation", "supply-chain", "defense-c2"}
REQUIRED_SHAPES = {
    "shapes/kg_lifecycle.shacl.ttl",
    "shapes/semantic_mapping.shacl.ttl",
    "shapes/named_graph_governance.shacl.ttl",
    "shapes/sector_modules.shacl.ttl",
}
REQUIRED_POLICY_SURFACES = {
    "promotion_gate",
    "graph_access_policy",
    "trust_profile",
    "lifecycle_phase",
    "retention_policy",
    "provenance",
}
REQUIRED_CLOSURE_KEYS = {"inside_source", "outside_policy", "boundary_membrane", "feedback_surface"}
REQUIRED_GATE_FLAGS = {
    "shacl_failures_block_promotion",
    "named_graph_metadata_is_policy_input",
    "preserve_source_provenance",
    "do_not_rewrite_ontogenesis_semantics",
}


def main() -> int:
    errors: list[str] = []
    if not FIXTURE.is_file():
        print(f"missing fixture: {FIXTURE}")
        return 1

    try:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"invalid JSON: {exc}")
        return 1

    if data.get("contract") != "policy-fabric.semantic-enterprise.policy-input":
        errors.append("unexpected contract identifier")
    if data.get("version") != "0.1.0":
        errors.append("unexpected contract version")

    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        expected = {
            "repository": "SocioProphet/ontogenesis",
            "release": "semantic-enterprise-v0.1.0",
            "manifest_path": "manifests/semantic_enterprise_v0_1_manifest.json",
            "rollup_registry_path": "catalog/semantic_enterprise_v0_1_registry.ttl",
            "named_graph_fixture_path": "examples/named-graphs/semantic_sector_named_graphs.ttl",
        }
        for key, value in expected.items():
            if source.get(key) != value:
                errors.append(f"source.{key} expected {value!r}, got {source.get(key)!r}")

    gate_behavior = data.get("gate_behavior")
    if not isinstance(gate_behavior, dict):
        errors.append("gate_behavior must be an object")
    else:
        missing = REQUIRED_GATE_FLAGS.difference(gate_behavior)
        if missing:
            errors.append(f"gate_behavior missing keys: {sorted(missing)}")
        for key in REQUIRED_GATE_FLAGS.intersection(gate_behavior):
            if gate_behavior.get(key) is not True:
                errors.append(f"gate_behavior.{key} must be true")

    shapes = set(data.get("shape_modules") or [])
    if not REQUIRED_SHAPES.issubset(shapes):
        errors.append(f"shape_modules missing: {sorted(REQUIRED_SHAPES.difference(shapes))}")

    surfaces = set(data.get("policy_surfaces") or [])
    if not REQUIRED_POLICY_SURFACES.issubset(surfaces):
        errors.append(f"policy_surfaces missing: {sorted(REQUIRED_POLICY_SURFACES.difference(surfaces))}")

    named_graphs = data.get("named_graphs")
    if not isinstance(named_graphs, list):
        errors.append("named_graphs must be a list")
    else:
        sectors = {record.get("sector") for record in named_graphs if isinstance(record, dict)}
        if sectors != REQUIRED_SECTORS:
            errors.append(f"expected sectors {sorted(REQUIRED_SECTORS)}, got {sorted(sectors)}")
        for record in named_graphs:
            if not isinstance(record, dict):
                errors.append("named_graph record must be an object")
                continue
            sector = record.get("sector")
            if not str(record.get("source_path", "")).startswith("examples/scenarios/"):
                errors.append(f"{sector} source_path must point to examples/scenarios")
            if not str(record.get("graph_uri_fragment", "")).startswith("graphs/scenarios/"):
                errors.append(f"{sector} graph URI must point to graphs/scenarios")
            for key in ["access_class", "trust_level", "lifecycle_phase", "retention_policy"]:
                if not record.get(key):
                    errors.append(f"{sector} missing {key}")

    closure = data.get("closure_model")
    if not isinstance(closure, dict):
        errors.append("closure_model must be an object")
    else:
        missing = REQUIRED_CLOSURE_KEYS.difference(closure)
        if missing:
            errors.append(f"closure_model missing keys: {sorted(missing)}")
        for key in REQUIRED_CLOSURE_KEYS.intersection(closure):
            if not isinstance(closure.get(key), str) or not closure[key].strip():
                errors.append(f"closure_model.{key} must be a non-empty string")

    if errors:
        print("Semantic Enterprise policy-input validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Semantic Enterprise policy-input validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
