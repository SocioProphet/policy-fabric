#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "policy_fabric_diff_hygiene_gate_report_v0.schema.json"
CLEAN_EXAMPLE = ROOT / "examples" / "policy_fabric_diff_hygiene_gate_report_example.json"
BLOCKED_ENV_EXAMPLE = ROOT / "examples" / "policy_fabric_diff_hygiene_gate_blocked_env_example.json"

REQUIRED_TOP_LEVEL = {"apiVersion", "kind", "metadata", "spec"}
REQUIRED_METADATA = {"name", "repository", "pullRequest", "issueRef", "baseSha", "headSha", "generatedAt"}
REQUIRED_SPEC = {"lane", "verdict", "changedFiles", "thresholds", "findings", "requiredPrSections", "exceptionsUsed", "requiredActions"}
VALID_VERDICTS = {"allow", "warn", "block", "needs_exception"}
NON_BLOCKING_VERDICTS = {"allow", "warn"}
REQUIRED_PR_SECTIONS = {"summary", "changed-files", "validation", "known-gaps", "self-critique", "linked-issue", "policy-evidence"}
DENIED_PATH_PREFIXES = {
    ".venv/",
    ".venv-tools/",
    "venv/",
    "env/",
    "node_modules/",
    ".mypy_cache/",
    ".pytest_cache/",
    "__pycache__/",
    ".ruff_cache/",
    ".tox/",
    ".nox/",
    ".cache/",
    "dist/",
    "build/",
    "target/",
}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_common(data: dict[str, Any], label: str) -> None:
    missing_top = REQUIRED_TOP_LEVEL - set(data)
    require(not missing_top, f"{label}: missing top-level fields: {sorted(missing_top)}")
    require(data.get("apiVersion") == "policy.fabric.diff-hygiene/v0", f"{label}: invalid apiVersion")
    require(data.get("kind") == "DiffHygieneGateReport", f"{label}: invalid kind")

    metadata = data.get("metadata")
    require(isinstance(metadata, dict), f"{label}: metadata must be an object")
    missing_metadata = REQUIRED_METADATA - set(metadata)
    require(not missing_metadata, f"{label}: missing metadata fields: {sorted(missing_metadata)}")
    require(str(metadata.get("baseSha")), f"{label}: baseSha must not be empty")
    require(str(metadata.get("headSha")), f"{label}: headSha must not be empty")

    spec = data.get("spec")
    require(isinstance(spec, dict), f"{label}: spec must be an object")
    missing_spec = REQUIRED_SPEC - set(spec)
    require(not missing_spec, f"{label}: missing spec fields: {sorted(missing_spec)}")
    require(spec.get("lane") in {"pre-review", "pre-merge"}, f"{label}: invalid lane")
    require(spec.get("verdict") in VALID_VERDICTS, f"{label}: invalid verdict")

    changed_files = spec.get("changedFiles")
    require(isinstance(changed_files, dict), f"{label}: changedFiles must be an object")
    paths = changed_files.get("paths")
    require(isinstance(paths, list), f"{label}: changedFiles.paths must be a list")
    require(changed_files.get("count") == len(paths) or changed_files.get("count", 0) >= len(paths), f"{label}: changedFiles.count must cover listed paths")

    thresholds = spec.get("thresholds")
    require(isinstance(thresholds, dict), f"{label}: thresholds must be an object")
    denied_prefixes = set(thresholds.get("deniedPathPrefixes", []))
    missing_denied = sorted(DENIED_PATH_PREFIXES - denied_prefixes)
    require(not missing_denied, f"{label}: missing denied path prefixes: {missing_denied}")

    sections = spec.get("requiredPrSections")
    require(isinstance(sections, list), f"{label}: requiredPrSections must be a list")
    section_names = {section.get("name") for section in sections if isinstance(section, dict)}
    missing_sections = sorted(REQUIRED_PR_SECTIONS - section_names)
    require(not missing_sections, f"{label}: missing PR sections: {missing_sections}")

    findings = spec.get("findings")
    require(isinstance(findings, list), f"{label}: findings must be a list")
    for index, finding in enumerate(findings):
        require(isinstance(finding, dict), f"{label}: finding {index} must be an object")
        require(finding.get("rule"), f"{label}: finding {index} missing rule")
        require(finding.get("severity") in {"info", "warn", "block", "needs_exception"}, f"{label}: finding {index} invalid severity")
        require(finding.get("message"), f"{label}: finding {index} missing message")


def validate_clean_report(data: dict[str, Any]) -> None:
    validate_common(data, "clean report")
    spec = data["spec"]
    require(spec["verdict"] in NON_BLOCKING_VERDICTS, "clean report: verdict must be allow or warn")
    changed = spec["changedFiles"]
    thresholds = spec["thresholds"]
    allowed_total = thresholds["maxChangedFiles"] + thresholds["changedFileAllowance"]
    require(changed["count"] <= allowed_total, "clean report: changed file count exceeds allowance")
    denied_prefixes = tuple(thresholds["deniedPathPrefixes"])
    denied_hits = [path for path in changed["paths"] if path.startswith(denied_prefixes)]
    require(not denied_hits, f"clean report: denied path hits found: {denied_hits}")


def validate_blocked_env_report(data: dict[str, Any]) -> None:
    validate_common(data, "blocked env report")
    spec = data["spec"]
    require(spec["verdict"] == "block", "blocked env report: verdict must be block")
    changed = spec["changedFiles"]
    require(changed["count"] > spec["thresholds"]["maxChangedFiles"], "blocked env report: changed file count must exceed max")
    paths = changed["paths"]
    require(any(path.startswith(".venv-tools/") for path in paths), "blocked env report: expected .venv-tools/ path")
    severities = {finding["severity"] for finding in spec["findings"]}
    require("block" in severities, "blocked env report: must contain at least one blocking finding")
    rules = {finding["rule"] for finding in spec["findings"]}
    require("denied-generated-paths" in rules, "blocked env report: missing denied-generated-paths finding")


def main() -> int:
    try:
        for path in [SCHEMA, CLEAN_EXAMPLE, BLOCKED_ENV_EXAMPLE]:
            if not path.exists():
                return fail(f"missing {path}")
        schema = load_json(SCHEMA)
        require(schema.get("title") == "Policy Fabric Diff Hygiene Gate Report v0", "schema title mismatch")
        require(schema.get("properties", {}).get("apiVersion", {}).get("const") == "policy.fabric.diff-hygiene/v0", "schema apiVersion const mismatch")
        require(schema.get("properties", {}).get("kind", {}).get("const") == "DiffHygieneGateReport", "schema kind const mismatch")

        validate_clean_report(load_json(CLEAN_EXAMPLE))
        validate_blocked_env_report(load_json(BLOCKED_ENV_EXAMPLE))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")
    except ValueError as exc:
        return fail(str(exc))

    print("OK: validated diff hygiene gate report schema and fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
