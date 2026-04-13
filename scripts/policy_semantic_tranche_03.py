from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def selector_identity(selector: dict[str, Any]) -> str:
    selector_type = selector.get("type")
    if selector_type in {"jsonpath", "xpath", "pointer"}:
        return f"{selector_type}:{selector.get('path', '')}"
    if selector_type == "regex":
        return f"regex:{selector.get('pattern', '')}:{selector.get('flags', '')}"
    if selector_type == "schemaRef":
        return f"schemaRef:{selector.get('schemaRef', '')}"
    return f"id:{selector.get('id', '')}"


def normalized_selector_value(selector: dict[str, Any]) -> tuple[str, str]:
    selector_type = selector.get("type", "")
    if selector_type in {"jsonpath", "xpath", "pointer"}:
        raw = selector.get("path", "").strip()
    elif selector_type == "regex":
        raw = selector.get("pattern", "").strip()
    else:
        raw = selector.get("schemaRef", "").strip()

    norm = raw
    if selector_type in {"jsonpath", "xpath"}:
        norm = norm.replace("[*]", "[]")
        norm = re.sub(r"\[\d+\]", "[]", norm)
    elif selector_type == "pointer":
        norm = re.sub(r"/\d+(?=/|$)", "/[]", norm)
    elif selector_type == "regex":
        norm = raw.strip("^$").strip()

    return selector_type, norm


def selector_may_overmatch(selector: dict[str, Any]) -> bool:
    selector_type, norm = normalized_selector_value(selector)
    raw = selector.get("path", "") or selector.get("pattern", "") or selector.get("schemaRef", "")
    if selector_type in {"jsonpath", "xpath"}:
        return "[*]" in raw or "[]" in norm
    if selector_type == "pointer":
        return "[]" in norm
    if selector_type == "regex":
        pattern = selector.get("pattern", "")
        return not (pattern.startswith("^") and pattern.endswith("$"))
    return False


def scope_values(rule: dict[str, Any], key: str) -> set[str]:
    when = rule.get("when", {}) or {}
    if key == "mode":
        value = when.get("mode")
        return {value} if value else {"*"}
    value = when.get(key)
    if value is None:
        return {"*"}
    if isinstance(value, list):
        return set(value) if value else {"*"}
    return {str(value)}


def scope_overlap(left: set[str], right: set[str]) -> bool:
    if "*" in left or "*" in right:
        return True
    return bool(left & right)


def scope_superset(left: set[str], right: set[str]) -> bool:
    if "*" in left:
        return True
    if "*" in right:
        return "*" in left
    return right <= left


def rule_scope_overlap(left_rule: dict[str, Any], right_rule: dict[str, Any]) -> bool:
    for key in ("mode", "environmentIn", "routeIn", "purposeIn"):
        if not scope_overlap(scope_values(left_rule, key), scope_values(right_rule, key)):
            return False
    return True


def rule_scope_subsumes(left_rule: dict[str, Any], right_rule: dict[str, Any]) -> bool:
    strict = False
    for key in ("mode", "environmentIn", "routeIn", "purposeIn"):
        left = scope_values(left_rule, key)
        right = scope_values(right_rule, key)
        if not scope_superset(left, right):
            return False
        if left != right:
            strict = True
    return strict


def classify_rule_pair(selector_id: str, left_rule: dict[str, Any], right_rule: dict[str, Any]) -> dict[str, Any] | None:
    if not rule_scope_overlap(left_rule, right_rule):
        return None

    left_sig = (
        left_rule.get("transform", {}).get("type"),
        left_rule.get("transform", {}).get("provider"),
        left_rule.get("transform", {}).get("capabilityRef"),
    )
    right_sig = (
        right_rule.get("transform", {}).get("type"),
        right_rule.get("transform", {}).get("provider"),
        right_rule.get("transform", {}).get("capabilityRef"),
    )

    if left_rule.get("priority", 0) == right_rule.get("priority", 0) and left_sig != right_sig:
        return {
            "code": "PFV021_RULE_PRECEDENCE_CONFLICT",
            "message": f"{selector_id}: same-priority overlapping rules {left_rule.get('id')} and {right_rule.get('id')} conflict",
        }

    left_subsumes = rule_scope_subsumes(left_rule, right_rule)
    right_subsumes = rule_scope_subsumes(right_rule, left_rule)

    if left_subsumes or right_subsumes:
        wider, narrower = (left_rule, right_rule) if left_subsumes else (right_rule, left_rule)
        if wider.get("priority", 0) >= narrower.get("priority", 0) and left_sig != right_sig:
            return {
                "code": "PFV025_ROLLOUT_SHADOW_CONFLICT",
                "message": f"{selector_id}: wider-scope rule {wider.get('id')} shadows narrower rule {narrower.get('id')}",
            }
        return {
            "code": "PFV024_ROLLOUT_SUBSUMPTION_WARNING",
            "message": f"{selector_id}: rule {wider.get('id')} subsumes {narrower.get('id')} across active scope",
        }

    if left_sig != right_sig:
        return {
            "code": "PFV020_RULE_PRECEDENCE_REQUIRED",
            "message": f"{selector_id}: overlapping rules {left_rule.get('id')} and {right_rule.get('id')} need explicit precedence semantics",
        }

    return None


def collect_tranche3_findings(policy: dict[str, Any]) -> list[dict[str, Any]]:
    selectors = policy.get("selectors", [])
    rules = [rule for rule in policy.get("rules", []) if rule.get("enabled", True) is not False]
    selectors_by_id = {selector["id"]: selector for selector in selectors if selector.get("id")}

    findings: list[dict[str, Any]] = []

    for selector in selectors:
        expected = selector.get("expectedCardinality")
        if not expected:
            findings.append({
                "code": "PFV023_SELECTOR_CARDINALITY_UNDERSPECIFIED",
                "message": f"selector {selector.get('id')} is missing expectedCardinality",
            })
        elif expected in {"zeroOrOne", "exactlyOne"} and selector_may_overmatch(selector):
            findings.append({
                "code": "PFV022_SELECTOR_CARDINALITY_OVERMATCH",
                "message": f"selector {selector.get('id')} may overmatch relative to declared cardinality {expected}",
            })

    grouped: dict[str, list[dict[str, Any]]] = {}
    for rule in rules:
        selector = selectors_by_id.get(rule.get("match", {}).get("selectorRef"))
        if not selector:
            continue
        identity = selector_identity(selector)
        grouped.setdefault(identity, []).append(rule)

    for identity, grouped_rules in grouped.items():
        if len(grouped_rules) <= 1:
            continue
        ordered = sorted(grouped_rules, key=lambda item: item.get("priority", 0))
        for i, left_rule in enumerate(ordered):
            for right_rule in ordered[i + 1 :]:
                finding = classify_rule_pair(identity, left_rule, right_rule)
                if finding:
                    findings.append(finding)

    return findings


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    policy = json.loads((root / "examples/policy_fabric_policy_v2_enhanced_example.json").read_text())
    print(json.dumps({"findings": collect_tranche3_findings(policy)}, indent=2))
