#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "sourceos-repo-context-policy.schema.json"
EXAMPLE = ROOT / "examples" / "sourceos" / "sourceos-repo-context-read-only.policy.json"

REQUIRED_DENIED = {
    "repo.write",
    "hooks.install",
    "hooks.modify",
    "dashboard.expose",
    "pty.spawn",
    "memory.persist.native",
    "network.callback",
    "external.update_check",
    "external.feedback_submit",
    "desktop.search.bypass_lampstand",
    "home.scan.unbounded",
    "system.scan",
    "symlink.follow",
}

REQUIRED_ALLOWED = {
    "repo.tree.read",
    "repo.stats.read",
    "repo.git_status.read",
    "repo.security_scan.read",
    "lampstand.project_root.consume",
    "lampstand.search_record.publish.local",
    "memory_mesh.promotion_packet.emit",
    "sherlock.adapter_record_search.emit",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    schema = load_json(SCHEMA)
    policy = load_json(EXAMPLE)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(policy), key=lambda error: list(error.path))
    if errors:
        print("SourceOS repo context policy failed validation:")
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f" - {location}: {error.message}")
        return 1

    allowed = set(policy["allowedCapabilities"])
    denied = set(policy["deniedCapabilities"])

    missing_allowed = sorted(REQUIRED_ALLOWED - allowed)
    if missing_allowed:
        print(f"Missing required allowed capabilities: {missing_allowed}")
        return 1

    missing_denied = sorted(REQUIRED_DENIED - denied)
    if missing_denied:
        print(f"Missing required denied capabilities: {missing_denied}")
        return 1

    overlap = sorted(allowed & denied)
    if overlap:
        print(f"Capabilities cannot be both allowed and denied: {overlap}")
        return 1

    if policy["pathRules"]["defaultDecision"] != "deny":
        print("Path default decision must remain deny")
        return 1
    if "~/dev/**" not in policy["pathRules"]["allow"]:
        print("Policy must allow ~/dev/** as the bounded development root")
        return 1
    if "~/**" not in policy["pathRules"]["deny"]:
        print("Policy must deny unbounded home scans")
        return 1

    scan = policy["scanRules"]
    if scan["followSymlinks"] is not False:
        print("scanRules.followSymlinks must remain false")
        return 1
    if scan["hiddenFilesDefault"] is not False:
        print("scanRules.hiddenFilesDefault must remain false")
        return 1
    if scan["securityScanMode"] != "advisory":
        print("securityScanMode must remain advisory")
        return 1

    lampstand = policy["lampstandRules"]
    if lampstand["desktopSearchAuthority"] != "lampstand":
        print("Lampstand must remain desktop/local search authority")
        return 1
    if lampstand["publishRawContent"] is not False:
        print("Lampstand raw content publication must remain false")
        return 1
    if lampstand["publishRequiresExplicitFlag"] is not True:
        print("Lampstand publish must require an explicit flag")
        return 1

    memory = policy["memoryMeshRules"]
    if memory["nativeSmartTreeMemoryPersistence"] is not False:
        print("Smart Tree native memory persistence must remain disabled")
        return 1
    if memory["promotionRequiresMemoryMesh"] is not True:
        print("Memory promotion must require Memory Mesh")
        return 1

    if policy["networkRules"]["allowedEndpoints"] != []:
        print("Network endpoints must remain denied by default")
        return 1
    if policy["writeRules"]["allowedOperations"] != []:
        print("Write operations must remain denied by default")
        return 1

    print("SourceOS repo context policy validates against schema and invariants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
