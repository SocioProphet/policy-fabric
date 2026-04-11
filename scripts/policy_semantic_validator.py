from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REIDENTIFY_TYPES = {"decrypt", "detokenize"}
IRREVERSIBLE_TYPES = {"redact", "hash"}
REVERSIBLE_TYPES = {"encrypt", "tokenize", "formatPreservingEncrypt", "formatPreservingTokenize", "decrypt", "detokenize"}
REQUIRED_AUDIT_FIELDS = {
    "tenantId",
    "policyId",
    "policyVersion",
    "planHash",
    "mode",
    "ruleHits",
    "selectorHits",
    "providerLatencyMs",
    "outcome",
}


def _load_json(path: Path):
    return json.loads(path.read_text())


def _finding(check_id: str, status: str, severity: str, code: str, message: str, artifact_ref: str | None = None) -> dict:
    item = {
        "id": check_id,
        "status": status,
        "severity": severity,
        "code": code,
        "message": message,
    }
    if artifact_ref:
        item["artifactRef"] = artifact_ref
    return item


def _ok(check_id: str, message: str, artifact_ref: str | None = None, code: str = "PFV000_POLICY_SEMANTICS_OK") -> dict:
    return _finding(check_id, "pass", "info", code, message, artifact_ref)


def _fail(check_id: str, code: str, message: str, artifact_ref: str | None = None) -> dict:
    return _finding(check_id, "fail", "error", code, message, artifact_ref)


def _warn(check_id: str, code: str, message: str, artifact_ref: str | None = None) -> dict:
    return _finding(check_id, "warn", "warn", code, message, artifact_ref)


def _duplicates(values: list[str]) -> list[str]:
    return sorted([value for value, count in Counter(values).items() if count > 1])


def _selector_identity(selector: dict) -> str:
    selector_type = selector.get("type")
    if selector_type in {"jsonpath", "xpath", "pointer"}:
        return f"{selector_type}:{selector.get('path', '')}"
    if selector_type == "regex":
        return f"regex:{selector.get('pattern', '')}:{selector.get('flags', '')}"
    if selector_type == "schemaRef":
        return f"schemaRef:{selector.get('schemaRef', '')}"
    return f"id:{selector.get('id', '')}"


def _normalized_selector_value(selector: dict) -> tuple[str, str]:
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


def _path_prefix_overlap(left: str, right: str) -> bool:
    return (
        left == right
        or left.startswith(right + ".")
        or left.startswith(right + "[")
        or left.startswith(right + "/")
        or right.startswith(left + ".")
        or right.startswith(left + "[")
        or right.startswith(left + "/")
    )


def _selector_overlap_reason(left: dict, right: dict) -> str | None:
    left_type, left_norm = _normalized_selector_value(left)
    right_type, right_norm = _normalized_selector_value(right)

    if left_type != right_type or not left_norm or not right_norm:
        return None

    if left_type in {"jsonpath", "xpath", "pointer"}:
        if left_norm == right_norm and _selector_identity(left) != _selector_identity(right):
            return "normalized-path-equivalence"
        if _path_prefix_overlap(left_norm, right_norm) and left_norm != right_norm:
            return "path-prefix-overlap"
        left_wild = re.sub(r"\[\d+\]", "[]", left_norm).replace("[*]", "[]")
        right_wild = re.sub(r"\[\d+\]", "[]", right_norm).replace("[*]", "[]")
        if left_wild == right_wild and left_norm != right_norm:
            return "wildcard-shadow"

    if left_type == "regex":
        if left_norm == right_norm and left.get("flags", "") == right.get("flags", "") and _selector_identity(left) != _selector_identity(right):
            return "regex-normalized-equivalence"
        shorter, longer = sorted([left_norm, right_norm], key=len)
        if shorter and len(shorter) >= 4 and shorter in longer:
            return "regex-shadow-heuristic"

    return None


def _subset_violations(scope_values: list[str], allowed_values: list[str] | None) -> list[str]:
    if not scope_values or not allowed_values or "*" in allowed_values:
        return []
    return sorted(set(scope_values) - set(allowed_values))


def collect_policy_semantic_findings(root: Path) -> list[dict]:
    findings: list[dict] = []
    policy_ref = 'examples/policy_fabric_policy_v2_enhanced_example.json'
    plan_ref = 'examples/policy_fabric_compiled_plan_example.json'
    catalog_ref = 'examples/policy_fabric_capability_catalog_example.json'
    policy = _load_json(root / policy_ref)
    plan = _load_json(root / plan_ref)
    catalog = _load_json(root / catalog_ref)

    providers = catalog.get('providers', [])
    capabilities = catalog.get('capabilities', [])
    provider_ids = [provider.get('id', '') for provider in providers]
    capability_ids = [capability.get('id', '') for capability in capabilities]
    dup_provider_ids = _duplicates(provider_ids)
    dup_capability_ids = _duplicates(capability_ids)
    if dup_provider_ids:
        findings.append(_fail('catalog:duplicate-providers', 'PFCAT001', f'duplicate provider ids: {dup_provider_ids}', catalog_ref))
    else:
        findings.append(_ok('catalog:duplicate-providers', 'capability catalog provider ids are unique', catalog_ref, 'PFCAT000_CATALOG_SEMANTICS_OK'))
    if dup_capability_ids:
        findings.append(_fail('catalog:duplicate-capabilities', 'PFCAT002', f'duplicate capability ids: {dup_capability_ids}', catalog_ref))
    else:
        findings.append(_ok('catalog:duplicate-capabilities', 'capability catalog capability ids are unique', catalog_ref, 'PFCAT000_CATALOG_SEMANTICS_OK'))

    providers_by_id = {provider['id']: provider for provider in providers if provider.get('id')}
    capabilities_by_id = {capability['id']: capability for capability in capabilities if capability.get('id')}

    catalog_capability_failures = []
    for capability in capabilities:
        provider = providers_by_id.get(capability.get('provider'))
        if not provider:
            catalog_capability_failures.append(f"capability {capability.get('id')} references unknown provider {capability.get('provider')}")
            continue
        if capability.get('transformType') not in provider.get('allowedTransformTypes', []):
            catalog_capability_failures.append(
                f"capability {capability.get('id')} transform {capability.get('transformType')} not allowed by provider {provider.get('id')}"
            )
    if catalog_capability_failures:
        code = 'PFCAT003' if any('unknown provider' in msg for msg in catalog_capability_failures) else 'PFCAT004'
        findings.append(_fail('catalog:provider-resolution', code, '; '.join(catalog_capability_failures), catalog_ref))
    else:
        findings.append(_ok('catalog:provider-resolution', 'capability catalog provider references and transform types are internally consistent', catalog_ref, 'PFCAT000_CATALOG_SEMANTICS_OK'))

    selectors = policy.get('selectors', [])
    rules = [rule for rule in policy.get('rules', []) if rule.get('enabled', True) is not False]
    selector_ids = [selector.get('id', '') for selector in selectors]
    rule_ids = [rule.get('id', '') for rule in rules]
    dup_selector_ids = _duplicates(selector_ids)
    dup_rule_ids = _duplicates(rule_ids)
    if dup_selector_ids:
        findings.append(_fail('policy:duplicate-selectors', 'PFV001', f'duplicate selector ids: {dup_selector_ids}', policy_ref))
    else:
        findings.append(_ok('policy:duplicate-selectors', 'policy selector ids are unique', policy_ref))
    if dup_rule_ids:
        findings.append(_fail('policy:duplicate-rules', 'PFV002', f'duplicate rule ids: {dup_rule_ids}', policy_ref))
    else:
        findings.append(_ok('policy:duplicate-rules', 'policy rule ids are unique', policy_ref))

    selectors_by_id = {selector['id']: selector for selector in selectors if selector.get('id')}
    missing_selector_refs = sorted({rule.get('match', {}).get('selectorRef') for rule in rules if rule.get('match', {}).get('selectorRef') not in selectors_by_id})
    if missing_selector_refs:
        findings.append(_fail('policy:selector-refs', 'PFV003', f'unresolved selector refs: {missing_selector_refs}', policy_ref))
    else:
        findings.append(_ok('policy:selector-refs', 'all enabled rule selectorRef values resolve to declared selectors', policy_ref))

    rollout = policy.get('rollout') or {}
    labels = policy.get('labels') or {}
    rollout_errors = []
    if policy.get('status') == 'approved':
        for field in ('tenants', 'environments', 'regions'):
            if not rollout.get(field):
                rollout_errors.append(f'approved policy requires non-empty rollout.{field}')
    if rollout_errors:
        findings.append(_fail('policy:rollout-scope', 'PFV006', '; '.join(rollout_errors), policy_ref))
    else:
        findings.append(_ok('policy:rollout-scope', 'approved policy rollout scope is present and non-empty where required', policy_ref))

    authorization_failures = []
    reidentify_failures = []
    for rule in rules:
        transform = rule.get('transform', {})
        rule_id = rule.get('id', '<unknown-rule>')
        provider_id = transform.get('provider')
        capability_id = transform.get('capabilityRef')
        transform_type = transform.get('type')
        provider = providers_by_id.get(provider_id)
        capability = capabilities_by_id.get(capability_id)
        if not provider:
            authorization_failures.append(f'rule {rule_id} references unknown provider {provider_id}')
            continue
        if transform_type not in provider.get('allowedTransformTypes', []):
            authorization_failures.append(f'rule {rule_id} transform {transform_type} not allowed by provider {provider_id}')
        if not capability:
            authorization_failures.append(f'rule {rule_id} references unknown capability {capability_id}')
            continue
        if capability.get('provider') != provider_id:
            authorization_failures.append(f'rule {rule_id} capability {capability_id} belongs to provider {capability.get("provider")}, not {provider_id}')
        if capability.get('transformType') != transform_type:
            authorization_failures.append(f'rule {rule_id} capability {capability_id} is for transform {capability.get("transformType")}, not {transform_type}')

        bad_tenants = _subset_violations(rollout.get('tenants', []), provider.get('allowedTenants'))
        bad_regions = _subset_violations(rollout.get('regions', []), provider.get('allowedRegions'))
        if bad_tenants:
            authorization_failures.append(f'rule {rule_id} rollout tenants outside provider {provider_id} allow-list: {bad_tenants}')
        if bad_regions:
            authorization_failures.append(f'rule {rule_id} rollout regions outside provider {provider_id} allow-list: {bad_regions}')

        bad_cap_tenants = _subset_violations(rollout.get('tenants', []), capability.get('allowedTenants'))
        bad_cap_regions = _subset_violations(rollout.get('regions', []), capability.get('allowedRegions'))
        if bad_cap_tenants:
            authorization_failures.append(f'rule {rule_id} rollout tenants outside capability {capability_id} allow-list: {bad_cap_tenants}')
        if bad_cap_regions:
            authorization_failures.append(f'rule {rule_id} rollout regions outside capability {capability_id} allow-list: {bad_cap_regions}')

        if transform_type in REIDENTIFY_TYPES:
            if policy.get('status') != 'approved':
                reidentify_failures.append(f'rule {rule_id} uses {transform_type} but policy status is {policy.get("status")}')
            if labels.get('reidentificationApproved') != 'true':
                reidentify_failures.append(f'rule {rule_id} uses {transform_type} without labels.reidentificationApproved=true')
            if labels.get('trustBoundary') != 'isolated-reidentify':
                reidentify_failures.append(f'rule {rule_id} uses {transform_type} without labels.trustBoundary=isolated-reidentify')
            if capability and not capability.get('reidentification', False):
                reidentify_failures.append(f'rule {rule_id} uses {transform_type} with non-reidentification capability {capability_id}')
            for key, value in (capability.get('requiredLabels') or {}).items() if capability else []:
                if labels.get(key) != value:
                    reidentify_failures.append(f'rule {rule_id} missing required label {key}={value} for capability {capability_id}')

    if authorization_failures:
        findings.append(_fail('policy:provider-capability-authorization', 'PFV004', '; '.join(authorization_failures), policy_ref))
    else:
        findings.append(_ok('policy:provider-capability-authorization', 'enabled rules use authorized provider and capability pairs within rollout scope', policy_ref))

    if reidentify_failures:
        findings.append(_fail('policy:reidentify-governance', 'PFV005', '; '.join(reidentify_failures), policy_ref))
    else:
        findings.append(_ok('policy:reidentify-governance', 're-identification boundary rules are satisfied or no re-identification transforms are present', policy_ref))

    selector_groups: dict[str, list[dict]] = defaultdict(list)
    for rule in rules:
        selector = selectors_by_id.get(rule.get('match', {}).get('selectorRef'))
        if selector:
            selector_groups[_selector_identity(selector)].append(rule)

    conflict_messages = []
    illegal_chain_messages = []
    for identity, grouped_rules in selector_groups.items():
        if len(grouped_rules) <= 1:
            continue
        ordered = sorted(grouped_rules, key=lambda item: item.get('priority', 0))
        signatures = {(r.get('transform', {}).get('type'), r.get('transform', {}).get('provider'), r.get('transform', {}).get('capabilityRef')) for r in ordered}
        if len(ordered) > 1:
            conflict_messages.append(f'{identity} is targeted by multiple enabled rules: {[r.get("id") for r in ordered]}')
        irreversible_seen = False
        for rule in ordered:
            transform_type = rule.get('transform', {}).get('type')
            if irreversible_seen and transform_type in REIDENTIFY_TYPES:
                illegal_chain_messages.append(f'{identity} attempts {transform_type} after irreversible transform chain {[r.get("id") for r in ordered]}')
            if transform_type in IRREVERSIBLE_TYPES:
                irreversible_seen = True
        if len(signatures) == 1 and not illegal_chain_messages:
            conflict_messages.append(f'{identity} is targeted redundantly by repeated transform signature {next(iter(signatures))}')

    overlap_messages: dict[str, list[str]] = defaultdict(list)
    indexed_rules = [
        (rule, selectors_by_id.get(rule.get('match', {}).get('selectorRef')))
        for rule in rules
    ]
    indexed_rules = [(rule, selector) for rule, selector in indexed_rules if selector]
    for i, (left_rule, left_selector) in enumerate(indexed_rules):
        for right_rule, right_selector in indexed_rules[i + 1:]:
            if _selector_identity(left_selector) == _selector_identity(right_selector):
                continue
            reason = _selector_overlap_reason(left_selector, right_selector)
            if reason:
                overlap_messages[reason].append(
                    f"{left_rule.get('id')} ({left_selector.get('id')}) overlaps {right_rule.get('id')} ({right_selector.get('id')}) via {reason}"
                )

    if conflict_messages:
        findings.append(_fail('policy:selector-conflicts', 'PFV007', '; '.join(conflict_messages), policy_ref))
    else:
        findings.append(_ok('policy:selector-conflicts', 'no enabled rules conflict on the same exact selector identity', policy_ref))

    overlap_checks = [
        ('normalized-path-equivalence', 'policy:selector-overlap-normalized', 'PFV011_SELECTOR_NORMALIZED_EQUIVALENCE', 'no normalized-path selector equivalence detected'),
        ('path-prefix-overlap', 'policy:selector-overlap-prefix', 'PFV012_SELECTOR_PATH_PREFIX_OVERLAP', 'no path-prefix selector overlap detected'),
        ('wildcard-shadow', 'policy:selector-overlap-wildcard', 'PFV013_SELECTOR_WILDCARD_SHADOW', 'no wildcard-shadow selector overlap detected'),
        ('regex-normalized-equivalence', 'policy:selector-overlap-regex-equivalence', 'PFV014_SELECTOR_REGEX_EQUIVALENCE', 'no regex normalized-equivalence detected'),
        ('regex-shadow-heuristic', 'policy:selector-overlap-regex-shadow', 'PFV015_SELECTOR_REGEX_SHADOW', 'no regex shadow-heuristic detected'),
    ]
    for reason, check_id, code, ok_message in overlap_checks:
        messages = overlap_messages.get(reason, [])
        if messages:
            findings.append(_warn(check_id, code, '; '.join(messages), policy_ref))
        else:
            findings.append(_ok(check_id, ok_message, policy_ref, 'PFV010_SELECTOR_OVERLAP_OK'))

    if illegal_chain_messages:
        findings.append(_fail('policy:illegal-transform-chains', 'PFV008', '; '.join(illegal_chain_messages), policy_ref))
    else:
        findings.append(_ok('policy:illegal-transform-chains', 'no illegal exact-target transform chains were detected', policy_ref))

    audit_nodes = [node for node in plan.get('nodes', []) if node.get('kind') == 'audit']
    attestation_failures = []
    if plan.get('sourcePolicy', {}).get('policyId') != policy.get('policyId') or plan.get('sourcePolicy', {}).get('version') != policy.get('version'):
        attestation_failures.append('compiled plan sourcePolicy does not match active authored policy id/version')
    if not audit_nodes:
        attestation_failures.append('compiled plan does not contain an audit node')
    else:
        audit_fields = set()
        for node in audit_nodes:
            audit_fields.update(node.get('config', {}).get('fields', []))
        missing_fields = sorted(REQUIRED_AUDIT_FIELDS - audit_fields)
        if missing_fields:
            attestation_failures.append(f'compiled plan audit fields missing required identifiers: {missing_fields}')
    if attestation_failures:
        findings.append(_fail('policy:attestation-readiness', 'PFV009', '; '.join(attestation_failures), plan_ref))
    else:
        findings.append(_ok('policy:attestation-readiness', 'compiled plan attestation fields are aligned to audit and explain requirements', plan_ref))

    tests = policy.get('tests', [])
    fixture_failures = []
    if policy.get('status') == 'approved' and not tests:
        fixture_failures.append('approved policy must include at least one test fixture')
    reversible_rules = [rule for rule in rules if rule.get('transform', {}).get('type') in REVERSIBLE_TYPES or rule.get('transform', {}).get('reversible') is True]
    attestation_assertions = [
        assertion
        for test in tests
        for assertion in test.get('assert', [])
        if assertion.get('target') == 'attestation'
    ]
    attestation_assertions.extend(
        assertion
        for test in tests
        for assertion in test.get('failureAttestation', [])
        if assertion.get('target') == 'attestation'
    )
    if reversible_rules and not attestation_assertions:
        fixture_failures.append('policy with reversible or provider-mediated transforms must include at least one attestation-targeted assertion')

    negative_fixture_failures = []
    negative_fixtures = [
        test for test in tests
        if test.get('expectFailure') is True
        or any(
            key in test
            for key in (
                'expectedFailureCode',
                'expectedFailingRule',
                'expectedFailingSelector',
                'expectedNoop',
                'failureAttestation',
            )
        )
    ]

    if policy.get('status') == 'approved' and not negative_fixtures:
        negative_fixture_failures.append('approved policy should include at least one negative fixture')

    for test in negative_fixtures:
        name = test.get('name', '<unnamed-fixture>')
        expected_noop = test.get('expectedNoop', False)
        has_failure_metadata = any(
            test.get(key) not in (None, [], "")
            for key in ('expectedFailureCode', 'expectedFailingRule', 'expectedFailingSelector', 'failureAttestation')
        )

        if expected_noop:
            if test.get('expectFailure', False):
                negative_fixture_failures.append(f'{name} declares both expectFailure=true and expectedNoop=true')
            if has_failure_metadata:
                negative_fixture_failures.append(f'{name} declares failure-specific metadata while marked expectedNoop=true')
        else:
            if not test.get('expectFailure', False):
                negative_fixture_failures.append(f'{name} declares failure metadata without expectFailure=true')
            if not has_failure_metadata:
                negative_fixture_failures.append(f'{name} expectFailure=true but no failure-specific expectations were declared')
            if test.get('expectedFailingRule') and test.get('expectedFailingRule') not in rule_ids:
                negative_fixture_failures.append(f'{name} references unknown expectedFailingRule {test.get("expectedFailingRule")}')
            if test.get('expectedFailingSelector') and test.get('expectedFailingSelector') not in selector_ids:
                negative_fixture_failures.append(f'{name} references unknown expectedFailingSelector {test.get("expectedFailingSelector")}')
            for assertion in test.get('failureAttestation', []):
                if assertion.get('target') != 'attestation':
                    negative_fixture_failures.append(f'{name} failureAttestation contains non-attestation assertion')

    if fixture_failures:
        findings.append(_fail('policy:test-readiness', 'PFV010', '; '.join(fixture_failures), policy_ref))
    else:
        findings.append(_ok('policy:test-readiness', 'policy fixtures cover approved-state minimums and attestation-aware assertions', policy_ref))

    if negative_fixture_failures:
        findings.append(_fail('policy:negative-fixtures', 'PFV018_NEGATIVE_FIXTURE_SEMANTICS_INVALID', '; '.join(negative_fixture_failures), policy_ref))
    else:
        findings.append(_ok('policy:negative-fixtures', 'negative fixtures are well formed across failure and no-op semantics', policy_ref, 'PFV017_NEGATIVE_FIXTURE_SEMANTICS_OK'))

    return findings


if __name__ == '__main__':
    import sys
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    findings = collect_policy_semantic_findings(root)
    print(json.dumps({"findings": findings}, indent=2))
    raise SystemExit(0 if not any(item['status'] == 'fail' for item in findings) else 1)
