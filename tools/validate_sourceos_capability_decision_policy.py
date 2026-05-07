#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "contracts" / "sourceos-capability-decision-policy.schema.json"
DEFAULT_POLICY = ROOT / "examples" / "sourceos" / "sourceos-capability-decision-baseline.policy.json"

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


def validate_schema(schema: dict, policy: dict) -> list[str]:
    errors: list[str] = []
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(policy), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return errors


def validate_invariants(policy: dict) -> list[str]:
    errors: list[str] = []

    if policy["defaultDecision"] != "deny":
        errors.append("Capability decision defaultDecision must remain deny")

    try:
        browser = service_class(policy, "sourceos.app.browser")
    except KeyError:
        errors.append("Missing browser service class: sourceos.app.browser")
        browser = None

    if browser is not None:
        if browser["authorityDomain"] != "app":
            errors.append("Browser service class must remain in app authority domain")
        if browser.get("emitsCanonicalEvents") is not True:
            errors.append("Browser service class must emit canonical events")
        if browser.get("requiresIncidentBundle") is not True:
            errors.append("Browser service class must require incident bundles")

        browser_required = set(browser["requiredCapabilities"])
        browser_optional = set(browser["optionalCapabilities"])
        browser_denied = set(browser["deniedCapabilities"])

        missing_browser_required = sorted(REQUIRED_BROWSER_REQUIRED - browser_required)
        if missing_browser_required:
            errors.append(f"Browser service class missing required capabilities: {missing_browser_required}")

        missing_browser_denied = sorted(REQUIRED_BROWSER_DENIED - browser_denied)
        if missing_browser_denied:
            errors.append(f"Browser service class missing denied capabilities: {missing_browser_denied}")

        browser_overlap = sorted((browser_required | browser_optional) & browser_denied)
        if browser_overlap:
            errors.append(f"Browser capabilities cannot be both allowed/optional and denied: {browser_overlap}")

    try:
        developer = service_class(policy, "sourceos.developer.terminal")
    except KeyError:
        errors.append("Missing developer terminal service class: sourceos.developer.terminal")
        developer = None

    if developer is not None:
        if developer["authorityDomain"] != "developer":
            errors.append("Developer terminal service class must remain in developer authority domain")
        if developer.get("emitsCanonicalEvents") is not True:
            errors.append("Developer terminal service class must emit canonical events")
        if developer.get("requiresIncidentBundle") is not True:
            errors.append("Developer terminal service class must require incident bundles")

        developer_denied = set(developer["deniedCapabilities"])
        missing_developer_denied = sorted(REQUIRED_DEVELOPER_DENIED - developer_denied)
        if missing_developer_denied:
            errors.append(f"Developer terminal service class missing denied capabilities: {missing_developer_denied}")

    codes = rule_codes(policy)
    missing_codes = sorted(REQUIRED_EXPLANATION_CODES - codes)
    if missing_codes:
        errors.append(f"Missing required explanation codes: {missing_codes}")

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
        errors.append(f"Missing required capability decision rules: {missing_pairs}")

    if policy["capabilityRules"]["requirePolicyTrace"] is not True:
        errors.append("capabilityRules.requirePolicyTrace must remain true")

    telemetry = policy["telemetryRules"]
    if telemetry["remoteDefault"] != "deny":
        errors.append("Remote telemetry default must remain deny")
    if telemetry["requiresExplicitGrant"] is not True:
        errors.append("Remote telemetry must require explicit grant")
    if telemetry["canonicalEventRequired"] is not True:
        errors.append("Telemetry policy decisions must require canonical events")

    identity = policy["identityRules"]
    if identity["upstreamProductIdentityLeak"] != "deny":
        errors.append("Upstream product identity leakage must remain denied")
    if identity["engineProvenanceAllowed"] is not True:
        errors.append("Engine provenance must remain allowed as provenance metadata")
    if identity["productSurfaceIdentityRequired"] is not True:
        errors.append("Product surface identity must remain required")

    launch = policy["launchRules"]
    if launch["inheritUserShell"] != "deny":
        errors.append("Packaged app shell inheritance must remain denied")
    if launch["duplicatePathEntries"] != "deny":
        errors.append("Duplicate launch PATH entries must remain denied")
    if launch["manifestRequiredForApps"] is not True:
        errors.append("App launch manifests must remain required")

    trust = policy["trustRules"]
    if trust["defaultTrustMode"] != "local_first":
        errors.append("Default trust mode must remain local_first")
    if trust["silentRemoteTrustLookup"] != "deny":
        errors.append("Silent remote trust lookup must remain denied")
    if trust["networkLookupRequiresPolicy"] is not True:
        errors.append("Network trust lookup must require policy")

    events = policy["eventRules"]
    if events["canonicalEventRequired"] is not True:
        errors.append("Canonical event requirement must remain true")
    if events["operatorNarrativeRequired"] is not True:
        errors.append("Operator narrative requirement must remain true")
    if events["causalityRequired"] is not True:
        errors.append("Causality requirement must remain true")
    if events["expectedDenialsSeverityMax"] != "notice":
        errors.append("Expected denials must not exceed notice severity by default")

    audit = policy["auditRules"]
    for key in ["requireDecisionId", "requireExplanationCode", "requireActor", "requireSubject", "requireRetentionClass"]:
        if audit[key] is not True:
            errors.append(f"auditRules.{key} must remain true")

    return errors


def validate(policy_path: Path, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    policy = load_json(policy_path)
    errors = validate_schema(schema, policy)
    if errors:
        return ["schema: " + error for error in errors]
    return validate_invariants(policy)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SourceOS capability decision policy")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="schema path")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY), help="policy example path")
    args = parser.parse_args()

    errors = validate(Path(args.policy), Path(args.schema))
    if errors:
        print("SourceOS capability decision policy failed validation:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("SourceOS capability decision policy validates against schema and invariants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
