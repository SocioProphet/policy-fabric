# Semantic Enterprise Policy Input v0.1

Policy Fabric consumes `semantic-enterprise-v0.1.0` from `SocioProphet/ontogenesis` as a policy-input surface for SHACL gates and named-graph governance metadata.

The local fixture is:

- `examples/semantic-enterprise/v0.1/policy-input.example.json`

The validator is:

- `tools/validate_semantic_enterprise_policy_input.py`

## Source release

- Repository: `SocioProphet/ontogenesis`
- Release/tag: `semantic-enterprise-v0.1.0`
- Manifest: `manifests/semantic_enterprise_v0_1_manifest.json`
- Rollup registry: `catalog/semantic_enterprise_v0_1_registry.ttl`
- Named graph fixture: `examples/named-graphs/semantic_sector_named_graphs.ttl`

## Policy input model

The v0.1 fixture models:

- SHACL gate modules
- named graph records for the five sector scenarios
- access class
- trust level
- lifecycle phase
- retention policy
- provenance-preservation requirements

## Gate behavior

Policy Fabric treats Semantic Enterprise v0.1 metadata as policy input. The fixture requires that:

- SHACL failures block promotion
- named graph metadata is a policy input
- source provenance is preserved
- Ontogenesis source semantics are not rewritten downstream

## Closure boundary

The fixture distinguishes:

- `inside_source`: authored semantic source modules and fixtures remain in Ontogenesis.
- `outside_policy`: Policy Fabric consumes gates and named-graph metadata as policy inputs.
- `boundary_membrane`: source path, registry reference, SHACL gate, named graph URI, access class, trust profile, lifecycle phase, and retention policy survive translation.
- `feedback_surface`: policy decisions and validation reports remain downstream evidence.

## Validation

Run:

```bash
make validate
```

or:

```bash
python3 tools/validate_semantic_enterprise_policy_input.py
```

## Parent work

- `SocioProphet/policy-fabric#65`
- `SocioProphet/delivery-excellence#21`
