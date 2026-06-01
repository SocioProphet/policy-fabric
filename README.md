# Policy Fabric

Policy Fabric is a governed platform for authoring, validating, packaging, and reviewing data-protection policy as code.

## Start here

- [Quickstart](docs/QUICKSTART.md)
- [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)
- [Trust and Security Model](docs/TRUST_AND_SECURITY_MODEL.md)
- [Agent Harness Policy Gate Model](docs/specs/agent-harness-policy-gates.md)
- [Support](SUPPORT.md)
- [FAQ](docs/FAQ.md)

## What this repository is

This repository is the **Policy Fabric Control Repository**.

It serves three roles:

1. Product contract surface — machine-readable schemas, examples, and validation artifacts for Policy Fabric.
2. Governance surface — repo-local rules, ownership contracts, reconcile logic, validation gates, and release expectations under `.policy-fabric/`.
3. Workflow surface — official AgentPlane repo-native workflow scaffolding under `.agentplane/`, integrated without replacing Policy Fabric’s own product model.

## What Policy Fabric does

Policy Fabric turns data-protection policy into a governed, testable, reviewable system.

It currently includes:

- authored policy contracts
- compiled execution plan contracts
- release pack, validation report, and replay report artifacts
- semantic validation for policy correctness and governance
- repo-native workflow and repair discipline
- GitHub-native collaboration and CI surfaces

## Current status

Current state: active buildout, with official AgentPlane successfully integrated into the control repo and repository health automation in place.

The repository is usable now, but the platform is still being shaped through semantic tranches. Expect active refinement of schemas, validator logic, examples, and release semantics.

## SourceOS repo context policy

Policy Fabric now carries the external policy contract for `sourceos.repo_context.read_only`, the policy profile used by Smart Tree / `sourceos-context` in the Lampstand, Sherlock, Memory Mesh, and AgentPlane integration lane.

The contract, example, and validator live at:

- `contracts/sourceos-repo-context-policy.schema.json`
- `examples/sourceos/sourceos-repo-context-read-only.policy.json`
- `tools/validate_sourceos_repo_context_policy.py`

Validate locally:

```bash
python -m pip install jsonschema
python tools/validate_sourceos_repo_context_policy.py
```

The policy preserves the required boundaries:

- only bounded `~/dev/**` repo roots are allowed;
- unbounded home, system, hidden-sensitive, and symlink traversal are denied;
- Lampstand remains the desktop/local search authority;
- raw content publication is denied;
- Lampstand publishing requires an explicit flag;
- Smart Tree native memory persistence is denied;
- Memory Mesh remains the durable memory authority;
- network callbacks and writes are denied by default.

## Repository map

- `contracts/` — active machine-readable contracts and schemas
- `examples/` — aligned examples for policies, plans, release packs, and reports
- `scripts/` — reconcile, doctor, semantic validation, branch audit, publish prep, and probe utilities
- `.policy-fabric/` — Policy Fabric governance and control surfaces
- `.agentplane/` — official AgentPlane workflow surfaces
- `docs/specs/` — normative design and tranche specifications
- `docs/assessments/` — architecture and integration assessments
- `docs/reports/` — generated operational and validation reports

## Quick start

Clone the repository and run the standard validation loop:

    python3 scripts/reconcile.py
    python3 scripts/doctor.py

If the change affects workflow, branch, AgentPlane, or GitHub surfaces, also run:

    python3 scripts/agentplane_probe.py
    python3 scripts/branch_audit.py
    python3 scripts/github_publish_prep.py

## Development workflow

- `main` is the stable baseline.
- risky or tranche-scoped work happens on `work/*` branches.
- generated artifacts are part of the control surface and should be refreshed through repo scripts.
- no branch should be treated as merge-ready until `python3 scripts/doctor.py` passes.

## Architecture and trust model

- [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)
- [Trust and Security Model](docs/TRUST_AND_SECURITY_MODEL.md)
- [Support](SUPPORT.md)

## Security

Do **not** report vulnerabilities in public issues.

See [SECURITY.md](SECURITY.md) for the reporting process and disclosure expectations.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch, validation, PR, and generated-artifact expectations.

## License

This repository is licensed under the [MIT License](LICENSE).

## Suggested GitHub description

Policy Fabric is a policy-governed data protection control repository for authored policies, compiled plans, release packs, and validation evidence.

## Suggested GitHub topics

- policy-fabric
- policy-as-code
- data-protection
- data-governance
- privacy-engineering
- control-plane
- semantic-validation
- agentplane
- security-governance
- release-engineering
