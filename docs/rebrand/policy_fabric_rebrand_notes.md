# Policy Fabric rebrand notes

This bundle intentionally presents the system as a new product informed by a prior reference design, not as a renamed continuation of the earlier project.

## Identity rules

- Product name: **Policy Fabric**
- Previous product branding: **retired from this bundle**
- Source framing: **prior reference design** or **2018 reference design**
- Core positioning: **data-protection policy platform with a compiled execution runtime**

## Vocabulary mapping

| Retired framing | New framing |
|---|---|
| old product name | Policy Fabric |
| modernization of prior project | new platform informed by prior reference design |
| masking service wrapper | Policy Fabric API |
| compiled masking graph | compiled execution plan |
| crypto/tokenization internals in app config | provider-backed capability references |
| unmask alongside mask | re-identification as a separate high-risk capability class |

## Namespace rules

- Policy schema version string: `policy.fabric/v2`
- Compiled-plan version string: `policy.fabric.plan/v1`
- Example service base URL: `https://policy-fabric.example.internal`
- File prefix: `policy_fabric_`

## Messaging rules

When describing lineage, say:
- “learned from a prior reference design”
- “preserved the useful execution kernel”
- “recast as a new product with new contracts, trust boundaries, and runtime semantics”

Avoid saying:
- “version 2 of the old project”
- “rebranded old product”
- “same platform under a new name”

## Practical consequence

The preserved ideas are architectural: processors, selectors, predicates, graphs, and policy-driven execution.
The product identity, trust model, API surface, and governance model are now those of Policy Fabric.
