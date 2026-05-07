#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "sourceos-capability-decision-policy.schema.json"
EXAMPLE = ROOT / "examples" / "sourceos" / "sourceos-capability-decision-baseline.policy.json"

REQUIRED_BROWSER_DENIED = {
    "telemetry.emit.remote.default",
    "ipc.lookup.cloud.sync.ambient",
    "identity.product.upstream_leak",
    "launch.inherit_user_shell",
}

REQUIRED_BROWSER_REQUIRED = {
    "browser.profile.read",
    "browser.renderer.spawn",
    "browser.gpu.spawn",
    "network.client.web",
    "diagnostics.local.incident",
    "events.canonical.emit",
}

REQUIRED_DEVELOPER_DENIED = {
    "telemetry.emit.remote.default",
    "privilege.escalation.untraced",
    "launch.inherit_user_shell.unbounded",
}

REQUIRED_EXPLANATION_CODES = {
    "CAPABILITY_ALLOWED_CANONICAL_EVENT_EMIT",
    "CAPABILITY_AUDIT_LOCAL_TELEMETRY",
    "CAPABILITY_ALLOWED_DEVELOPER_SESSION_PROVENANCE",
    "CAPABILITY_DENIED_REMOTE_TELEMETRY_DEFAULT",
    "CAPABILITY_DENIED_PRODUCT_IDENTITY_LEAK",
    "CAPABILITY_DENIED_INHERIT_USER_SHELL",
    "CAPABILITY_DENIED_UNTRACED_PRIVILEGE_ESCALATION",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> int:
    print(message)
    return 1


def service_class(policy: dict, name: str) -> dict:
    for item in policy["serviceClasses"]:
        if item["serviceClass"] == name:
            return item
    raise KeyError(name)


def rule_codes(policy: dict) -> set[str]:
    codes = set()
    for bucket in ("allow", "deny"):
        for rule in policy["capabilityRules"][bucket]:
            codes.add(rule["explanationCode"])
    return codes


def rule_pairs(policy: dict) -> set[tuple[str, str, str]]:
    pairs = set()
    for bucket in ("allow", "deny"):
        for rule in policy["capabilityRules"][bucket]:
            pairs.add((rule["capability"], rule["serviceClass"], rule["decision"]))
    return pairs


def main() -> int:
    schema = load_json(SCHEMA)
    policy = load_json(EXAMPLE)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(policy), key=lambda error: list(error.path))
    if errors:
        print("SourceOS capability decision policy failed schema validation:")
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f" - {location}: {error.message}")
        return 1

    if policy["defaultDecision"] != "deny":
        return fail("Capability decision defaultDecision must remain deny")

    browser = service_class(policy, "sourceos.app.browser")
    if browser["authorityDomain"] != "app":
        return fail("Browser service class must remain in app authority domain")
    if browser.get("emitsCanonicalEvents") is not True:
        return fail("Browser service class must emit canonical events")
    if browser.get("requiresIncidentBundle") is not True:
        return fail("Browser service class must require incident bundles")

    browser_required = set(browser["requiredCapabilities"])
    browser_optional = set(browser["optionalCapabilities"])
    browser_denied = set(browser["deniedCapabilities"])

    missing_browser_required = sorted(REQUIRED_BROWSER_REQUIRED - browser_required)
    if missing_browser_required:
        return fail(f"Browser service class missing required capabilities: {missing_browser_required}")

    missing_browser_denied = sorted(REQUIRED_BROWSER_DENIED - browser_denied)
    if missing_browser_denied:
        return fail(f"Browser service class missing denied capabilities: {missing_browser_denied}")

    browser_overlap = sorted((browser_required | browser_optional) & browser_denied)
    if browser_overlap:
        return fail(f"Browser capabilities cannot be both allowed/optional and denied: {browser_overlap}")

    developer = service_class(policy, "sourceos.developer.terminal")
    if developer["authorityDomain"] != "developer":
        return fail("Developer terminal service class must remain in developer authority domain")
    if developer.get("emitsCanonicalEvents") is not True:
        return fail("Developer terminal service class must emit canonical events")
    if developer.get("requiresIncidentBundle") is not True:
        return fail("Developer terminal service class must require incident bundles")

    developer_denied = set(developer["deniedCapabilities"])
    missing_developer_denied = sorted(REQUIRED_DEVELOPER_DENIED - developer_denied)
    if missing_developer_denied:
        return fail(f"Developer terminal service class missing denied capabilities: {missing_developer_denied}")

    codes = rule_codes(policy)
    missing_codes = sorted(REQUIRED_EXPLANATION_CODES - codes)
    if missing_codes:
        return fail(f"Missing required explanation codes: {missing_codes}")

    pairs = rule_pairs(policy)
    required_pairs = {
        ("telemetry.emit.remote.default", "sourceos.app.browser", "deny"),
        ("identity.product.upstream_leak", "sourceos.app.browser", "deny"),
        ("launch.inherit_user_shell", "sourceos.app.browser", "deny"),
        ("privilege.escalation.untraced", "sourceos.developer.terminal", "deny"),
        ("events.canonical.emit", "sourceos.app.browser", "allow"),
        ("developer.session.provenance", "sourceos.developer.terminal", "allow"),
    }
    missing_pairs = sorted(required_pairs - pairs)
    if missing_pairs:
        return fail(f"Missing required capability decision rules: {missing_pairs}")

    if policy["capabilityRules"]["requirePolicyTrace"] is not True:
        return fail("capabilityRules.requirePolicyTrace must remain true")

    telemetry = policy["telemetryRules"]
    if telemetry["remoteDefault"] != "deny":
        return fail("Remote telemetry default must remain deny")
    if telemetry["requiresExplicitGrant"] is not True:
        return fail("Remote telemetry must require explicit grant")
    if telemetry["canonicalEventRequired"] is not True:
        return fail("Telemetry policy decisions must require canonical events")

    identity = policy["identityRules"]
    if identity["upstreamProductIdentityLeak"] != "deny":
        return fail("Upstream product identity leakage must remain denied")
    if identity["engineProvenanceAllowed"] is not True:
        return fail("Engine provenance must remain allowed as provenance metadata")
    if identity["productSurfaceIdentityRequired"] is not True:
        return fail("Product surface identity must remain required")

    launch = policy["launchRules"]
    if launch["inheritUserShell"] != "deny":
        return fail("Packaged app shell inheritance must remain denied")
    if launch["duplicatePathEntries"] != "deny":
        return fail("Duplicate launch PATH entries must remain denied")
    if launch["manifestRequiredForApps"] is not True:
        return fail("App launch manifests must remain required")

    trust = policy["trustRules"]
    if trust["defaultTrustMode"] != "local_first":
        return fail("Default trust mode must remain local_first")
    if trust["silentRemoteTrustLookup"] != "deny":
        return fail("Silent remote trust lookup must remain denied")
    if trust["networkLookupRequiresPolicy"] is not True:
        return fail("Network trust lookup must require policy")

    events = policy["eventRules"]
    if events["canonicalEventRequired"] is not True:
        return fail("Canonical event requirement must remain true")
    if events["operatorNarrativeRequired"] is not True:
        return fail("Operator narrative requirement must remain true")
    if events["causalityRequired"] is not True:
        return fail("Causality requirement must remain true")
    if events["expectedDenialsSeverityMax"] != "notice":
        return fail("Expected denials must not exceed notice severity by default")

    audit = policy["auditRules"]
    for key in ["requireDecisionId", "requireExplanationCode", "requireActor", "requireSubject", "requireRetentionClass"]:
        if audit[key] is not True:
            return fail(f"auditRules.{key} must remain true")

    print("SourceOS capability decision policy validates against schema and invariants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
