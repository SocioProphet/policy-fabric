"""Purpose-admissibility gate — the consent-plane DECISION ENGINE (runtime).

The consent-plane so far had a decision *contract*
(`contracts/purpose_admissibility_gate_decision_v1.schema.json`) and a document
*validator* (`tools/validate_purpose_admissibility_gate.py`), but nothing that
actually read the catalogs and DECIDED. This is that engine: given a tool
invocation's (role, surface, space, tool, purpose[, consent]) it computes an
`admit`/`deny` decision, **fail-closed**, from the canonical catalogs in
socioprophet-agent-standards consent-plane/001, and emits a v1 decision document.

`enforce()` is the runtime call a surface makes before dispatching a tool: it
RAISES `ConsentDenied` on deny, so a disallowed invocation cannot proceed. This
is what turns E1 from "envelope declared in CI" into "invocation refused at run".

Admissibility (all must hold; deny reasons accumulate):
  1. the tool serves the declared purpose            (tool-purpose-bindings)
  2. the role admits the purpose                      (agent-roles)
  3. the surface allows it and does not deny it       (surfaces; deny WINS)
  4. the surface does not deny the target space       (surfaces.space_deny; containment)
  5. the role tolerates every blocking taint on the space, and crossing a
     data-namespace carries a per-tenant consent toleration (spaces; Art 6/7)
  6. per-purpose consent is present where the surface or tool requires it
Anything unknown (role/surface/space/tool/purpose, or a missing catalog) => deny.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required (python -m pip install pyyaml)") from exc

API_VERSION = "policy.fabric.consent-plane/v1"
KIND = "PurposeAdmissibilityGateDecision"

CATALOG_FILES = {
    "roles": "agent-roles_v1.yaml",
    "surfaces": "surfaces_v1.yaml",
    "spaces": "spaces_v1.yaml",
    "bindings": "tool-purpose-bindings_v1.yaml",
}
_BLOCKING_EFFECTS = {"NoEntry", "NoExecute"}
_VENDORED = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "consent-plane"


class ConsentDenied(Exception):
    """Raised by enforce() when the gate denies an invocation (fail-closed)."""

    def __init__(self, reasons: list[str], decision: dict[str, Any]):
        self.reasons = reasons
        self.decision = decision
        super().__init__("consent-plane deny: " + "; ".join(reasons))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ----------------------------------------------------------------------------- catalogs
def discover_catalog_root(explicit: str | None = None) -> Path | None:
    """Zero-config: explicit arg -> $PURPOSE_GATE_CATALOG_ROOT -> a sibling
    socioprophet-agent-standards checkout -> vendored fixtures. First hit wins;
    a miss returns None (the caller fails closed) — never a silent guess."""
    # An EXPLICIT root is honoured alone: a caller that names a root means it, so
    # a miss there fails closed rather than silently falling back to vendored.
    if explicit:
        candidates: list[Path] = [Path(explicit)]
    else:
        candidates = []
        env = os.environ.get("PURPOSE_GATE_CATALOG_ROOT")
        if env:
            candidates.append(Path(env))
        here = Path(__file__).resolve()
        for parent in here.parents:
            sib = parent / "socioprophet-agent-standards" / "standards" / "consent-plane"
            if sib.is_dir():
                candidates.append(sib)
                break
        candidates.append(_VENDORED)
    for c in candidates:
        if c.is_dir() and all((c / f).exists() for f in CATALOG_FILES.values()):
            return c
    return None


def load_catalogs(root: str | Path | None = None) -> dict[str, Any]:
    base = discover_catalog_root(str(root) if root else None)
    if base is None:
        raise ConsentDenied(
            ["consent-plane catalogs not found (fail-closed): set $PURPOSE_GATE_CATALOG_ROOT"],
            {},
        )
    cat: dict[str, Any] = {}
    for key, fname in CATALOG_FILES.items():
        cat[key] = yaml.safe_load((Path(base) / fname).read_text())
    return cat


def _index(catalogs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Turn the catalog lists into id->record maps for O(1) lookup."""
    roles = {r["id"]: r for r in catalogs["roles"]["spec"]["roles"]}
    surfaces = {s["id"]: s for s in catalogs["surfaces"]["spec"]["surfaces"]}
    spaces = {s["id"]: s for s in catalogs["spaces"]["spec"]["spaces"]}
    bindings = {b["tool"]: b for b in catalogs["bindings"]["spec"]["bindings"]}
    return {"roles": roles, "surfaces": surfaces, "spaces": spaces, "bindings": bindings}


# ----------------------------------------------------------------------------- evaluation
def _evaluate(req: dict[str, Any], idx: dict[str, dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    role = req.get("role")
    surface = req.get("surface")
    space = req.get("space")
    tool = req.get("tool")
    purpose = req.get("declaredPurpose")
    consent = req.get("consent") or {}
    granted_purposes = set(consent.get("purposes", []))
    granted_tenants = set(consent.get("tenants", []))
    granted_regions = set(consent.get("regions", []))

    role_rec = idx["roles"].get(role)
    surface_rec = idx["surfaces"].get(surface)
    space_rec = idx["spaces"].get(space)
    binding = idx["bindings"].get(tool)

    # 1. tool serves the declared purpose
    if binding is None:
        reasons.append(f"tool '{tool}' is not in the tool-purpose catalog (fail-closed)")
    elif purpose not in binding.get("purposes", []):
        reasons.append(f"tool '{tool}' does not serve purpose '{purpose}'")

    # 2. role admits the purpose
    if role_rec is None:
        reasons.append(f"unknown role '{role}' (fail-closed)")
    elif purpose not in role_rec.get("admissible", []):
        reasons.append(f"role '{role}' is not admissible for purpose '{purpose}'")

    # 3. surface allows it (deny wins) + 4. surface space containment
    if surface_rec is None:
        reasons.append(f"unknown surface '{surface}' (fail-closed)")
    else:
        if purpose in surface_rec.get("deny_purposes", []):
            reasons.append(f"surface '{surface}' denies purpose '{purpose}' (envelope)")
        elif purpose not in surface_rec.get("purposes", []):
            reasons.append(f"surface '{surface}' does not allow purpose '{purpose}'")
        if space in surface_rec.get("space_deny", []):
            reasons.append(f"surface '{surface}' denies space '{space}' (containment)")

    # 5. space taint tolerance
    if space_rec is None:
        reasons.append(f"unknown space '{space}' (fail-closed)")
    else:
        tolerations = set(role_rec.get("tolerations", [])) if role_rec else set()
        for taint in space_rec.get("taints", []):
            if taint.get("effect") not in _BLOCKING_EFFECTS:
                continue
            key, value = taint.get("key"), taint.get("value")
            if key == "tenant":
                tenant = req.get("tenant")
                if not tenant or tenant not in granted_tenants:
                    reasons.append(
                        f"space '{space}' requires a per-tenant consent toleration "
                        f"(GDPR Art 6/7); none for tenant '{tenant}'"
                    )
            elif key == "region":
                region = req.get("region")
                if not region or region not in granted_regions:
                    reasons.append(
                        f"space '{space}' requires a geographic-residency toleration "
                        f"(GDPR Ch. V cross-border transfer); none for region '{region}'"
                    )
            else:
                tol = f"{key}={value}"
                if tol not in tolerations:
                    reasons.append(f"role '{role}' does not tolerate taint '{tol}' on space '{space}'")

    # 6. per-purpose consent where required
    needs = False
    if surface_rec and surface_rec.get("consent_required") == "per-purpose":
        needs = True
    if binding and binding.get("consent_required") == "per-purpose":
        needs = True
    if needs and purpose not in granted_purposes:
        reasons.append(f"purpose '{purpose}' requires per-purpose consent; none granted")

    return reasons


def decide(request: dict[str, Any], catalogs: dict[str, Any]) -> dict[str, Any]:
    """Compute a v1 decision document for `request`. Fail-closed."""
    idx = _index(catalogs)
    reasons = _evaluate(request, idx)
    decision = "deny" if reasons else "admit"

    req_out = {
        k: request[k]
        for k in ("role", "surface", "space", "tool", "declaredPurpose", "tenant", "region", "context")
        if request.get(k) is not None
    }
    receipt = {
        "role": request.get("role"),
        "surface": request.get("surface"),
        "space": request.get("space"),
        "tool": request.get("tool"),
        "purpose": request.get("declaredPurpose"),
        "decision": decision,
    }
    seal = hashlib.sha256(
        json.dumps({"r": req_out, "d": decision, "why": reasons}, sort_keys=True).encode()
    ).hexdigest()[:16]
    doc: dict[str, Any] = {
        "apiVersion": API_VERSION,
        "kind": KIND,
        "metadata": {
            "name": f"gate-{decision}-{seal}",
            "generatedAt": _utc_now(),
            "subjectRef": request.get("subjectRef", "urn:agent:unknown"),
            "actionOntologyReceiptRef": f"receipt://consent-plane/{seal}",
        },
        "spec": {"request": req_out, "decision": decision, "receipt": receipt},
    }
    if decision == "deny":
        doc["spec"]["denyReasons"] = reasons  # non-empty; ABSENT on admit (contract)
    return doc


def enforce(request: dict[str, Any], catalogs: dict[str, Any] | None = None) -> dict[str, Any]:
    """The runtime guard: return the admit decision, or RAISE ConsentDenied.

    A surface calls this before dispatching a tool; a denied invocation cannot
    proceed. This is the fail-closed teeth at call time."""
    cat = catalogs if catalogs is not None else load_catalogs()
    doc = decide(request, cat)
    if doc["spec"]["decision"] == "deny":
        raise ConsentDenied(doc["spec"]["denyReasons"], doc)
    return doc


def _main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Purpose-admissibility gate (consent-plane decision engine).")
    ap.add_argument("--role", required=True)
    ap.add_argument("--surface", required=True)
    ap.add_argument("--space", required=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--purpose", required=True, dest="declaredPurpose")
    ap.add_argument("--tenant")
    ap.add_argument("--region", help="jurisdiction the operation targets (data-namespace residency)")
    ap.add_argument("--consent-purpose", action="append", default=[], help="a purpose consent was granted for")
    ap.add_argument("--consent-tenant", action="append", default=[], help="a tenant consent was granted for")
    ap.add_argument("--consent-region", action="append", default=[], help="a jurisdiction residency was granted for")
    ap.add_argument("--catalog-root")
    args = ap.parse_args(argv)
    request = {
        "role": args.role, "surface": args.surface, "space": args.space,
        "tool": args.tool, "declaredPurpose": args.declaredPurpose,
        "tenant": args.tenant, "region": args.region,
        "consent": {"purposes": args.consent_purpose, "tenants": args.consent_tenant,
                    "regions": args.consent_region},
    }
    try:
        catalogs = load_catalogs(args.catalog_root)
    except ConsentDenied as exc:
        print(json.dumps({"decision": "deny", "denyReasons": exc.reasons}), file=sys.stderr)
        return 3
    doc = decide(request, catalogs)
    print(json.dumps(doc, indent=2))
    return 0 if doc["spec"]["decision"] == "admit" else 3


if __name__ == "__main__":
    sys.exit(_main())
