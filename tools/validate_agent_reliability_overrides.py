#!/usr/bin/env python3
"""Validate SourceOS Agent Reliability inheritance and break-glass contracts.

This validator is intentionally dependency-free. It checks the first Policy
Fabric contract set consumed by guardrail-fabric and AgentPlane for scoped
policy inheritance and break-glass override semantics.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

INHERITANCE_SCHEMA = ROOT / "contracts" / "policy_fabric_agent_inheritance_profile_v1.schema.json"
BREAK_GLASS_SCHEMA = ROOT / "contracts" / "policy_fabric_break_glass_override_v1.schema.json"
INHERITANCE_EXAMPLE = ROOT / "examples" / "policy_fabric_agent_inheritance_profile_example.json"
BREAK_GLASS_EXAMPLE = ROOT / "examples" / "policy_fabric_break_glass_override_example.json"

EXPECTED_PRECEDENCE = ["enterprise", "organization", "repository", "local", "user", "runtime"]
TERMINAL_ACTION_CLASSES = {"shell", "filesystem", "git", "network", "model", "browser", "infra", "database", "package", "runtime", "unknown"}


def die(message: str) -> None:
    print(f"[agent-reliability-overrides] ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        die(f"missing file: {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        die(f"expected object in {path.relative_to(ROOT)}")
    return data


def require_keys(obj: dict[str, Any], keys: list[str], path: str) -> None:
    missing = [key for key in keys if key not in obj]
    if missing:
        die(f"{path} missing required keys: {missing}")


def parse_dt(value: str, path: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        die(f"{path} must be ISO-8601 datetime: {value}")
        raise exc


def validate_schema_shape() -> None:
    inheritance_schema = load_json(INHERITANCE_SCHEMA)
    break_glass_schema = load_json(BREAK_GLASS_SCHEMA)

    require_keys(inheritance_schema, ["$schema", "title", "type", "required", "properties"], "inheritance schema")
    require_keys(break_glass_schema, ["$schema", "title", "type", "required", "properties"], "break-glass schema")

    for field in ["apiVersion", "kind", "metadata", "spec"]:
        if field not in inheritance_schema.get("required", []):
            die(f"inheritance schema required missing {field}")
    for field in ["apiVersion", "kind", "metadata", "spec", "status"]:
        if field not in break_glass_schema.get("required", []):
            die(f"break-glass schema required missing {field}")


def validate_inheritance_profile(profile: dict[str, Any]) -> None:
    require_keys(profile, ["apiVersion", "kind", "metadata", "spec"], "inheritance profile")
    if profile["apiVersion"] != "policy.fabric.agent-inheritance/v1":
        die("inheritance profile apiVersion mismatch")
    if profile["kind"] != "AgentPolicyInheritanceProfile":
        die("inheritance profile kind mismatch")

    spec = profile["spec"]
    require_keys(spec, ["scopePrecedence", "conflictResolution", "layers", "breakGlass"], "inheritance profile spec")
    if spec["conflictResolution"] != "stricter-wins":
        die("inheritance profile must use stricter-wins conflict resolution")
    if spec["scopePrecedence"] != EXPECTED_PRECEDENCE:
        die(f"unexpected scope precedence: {spec['scopePrecedence']}")

    layers = spec["layers"]
    if not isinstance(layers, list) or not layers:
        die("inheritance profile layers must be a non-empty list")

    seen = set()
    for index, layer in enumerate(layers):
        require_keys(layer, ["scope", "policyRef", "canTighten", "canWeakenHigherScope"], f"layer[{index}]")
        scope = layer["scope"]
        if scope in seen:
            die(f"duplicate inheritance layer scope: {scope}")
        seen.add(scope)
        if scope not in EXPECTED_PRECEDENCE:
            die(f"unsupported inheritance scope: {scope}")
        if layer["canTighten"] is not True:
            die(f"layer {scope} must be able to tighten controls")
        if layer["canWeakenHigherScope"] is not False:
            die(f"layer {scope} must not weaken higher-scope controls")
        if layer.get("requiresAudit") is not True:
            die(f"layer {scope} must require audit")
        if layer.get("failClosed") is not True:
            die(f"layer {scope} must fail closed")
        if not layer.get("forceEnabledPolicies"):
            die(f"layer {scope} must force-enable at least one policy")

    if "enterprise" not in seen or "repository" not in seen or "runtime" not in seen:
        die("inheritance profile must include enterprise, repository, and runtime layers")

    break_glass = spec["breakGlass"]
    require_keys(
        break_glass,
        ["allowed", "requiresHumanApprover", "requiresExpiry", "requiresReason", "requiresAuditRef", "maxDurationMinutes", "allowedActionClasses"],
        "inheritance profile breakGlass",
    )
    if break_glass["allowed"] is not True:
        die("break-glass must be explicitly allowed in the profile")
    for flag in ["requiresHumanApprover", "requiresExpiry", "requiresReason", "requiresAuditRef"]:
        if break_glass[flag] is not True:
            die(f"break-glass profile must set {flag}=true")
    if not isinstance(break_glass["maxDurationMinutes"], int) or break_glass["maxDurationMinutes"] <= 0:
        die("break-glass maxDurationMinutes must be positive")
    unknown_classes = set(break_glass["allowedActionClasses"]) - TERMINAL_ACTION_CLASSES
    if unknown_classes:
        die(f"break-glass profile contains unsupported action classes: {sorted(unknown_classes)}")


def validate_break_glass_override(override: dict[str, Any], profile: dict[str, Any]) -> None:
    require_keys(override, ["apiVersion", "kind", "metadata", "spec", "status"], "break-glass override")
    if override["apiVersion"] != "policy.fabric.break-glass/v1":
        die("break-glass override apiVersion mismatch")
    if override["kind"] != "BreakGlassOverride":
        die("break-glass override kind mismatch")

    metadata = override["metadata"]
    spec = override["spec"]
    status = override["status"]
    require_keys(metadata, ["overrideId", "createdAt", "expiresAt"], "break-glass metadata")
    require_keys(spec, ["approver", "scope", "actionClass", "resource", "reason", "auditRef", "constraints"], "break-glass spec")
    require_keys(status, ["state", "usedCount"], "break-glass status")

    created = parse_dt(metadata["createdAt"], "metadata.createdAt")
    expires = parse_dt(metadata["expiresAt"], "metadata.expiresAt")
    if expires <= created:
        die("break-glass expiresAt must be after createdAt")

    profile_limit = profile["spec"]["breakGlass"].get("maxDurationMinutes")
    duration_minutes = int((expires - created).total_seconds() // 60)
    if duration_minutes > profile_limit:
        die(f"break-glass duration {duration_minutes}m exceeds profile max {profile_limit}m")

    approver = spec["approver"]
    require_keys(approver, ["id", "type"], "break-glass approver")
    if approver["type"] != "human":
        die("break-glass approver must be human for SourceOS Agent Reliability")
    if not spec["reason"].strip():
        die("break-glass reason must be non-empty")
    if not spec["auditRef"].strip():
        die("break-glass auditRef must be non-empty")

    action_class = spec["actionClass"]
    allowed = set(profile["spec"]["breakGlass"].get("allowedActionClasses", []))
    if action_class not in allowed:
        die(f"break-glass action class {action_class} is not allowed by inheritance profile")

    constraints = spec["constraints"]
    require_keys(constraints, ["singleUse", "maxUses", "allowedCommands", "allowedPaths", "allowedProviders"], "break-glass constraints")
    if constraints["singleUse"] is True and constraints["maxUses"] != 1:
        die("single-use break-glass override must have maxUses=1")
    if status["usedCount"] > constraints["maxUses"]:
        die("break-glass usedCount exceeds maxUses")
    if status["state"] == "active" and status["usedCount"] >= constraints["maxUses"]:
        die("active break-glass override cannot have usedCount >= maxUses")
    if spec.get("signature") is None:
        die("break-glass override must include a signature object, even if placeholder/dev")


def main() -> int:
    validate_schema_shape()
    inheritance = load_json(INHERITANCE_EXAMPLE)
    override = load_json(BREAK_GLASS_EXAMPLE)
    validate_inheritance_profile(inheritance)
    validate_break_glass_override(override, inheritance)
    print("[agent-reliability-overrides] OK: inheritance and break-glass contracts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
