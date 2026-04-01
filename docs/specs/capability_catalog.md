# Capability Catalog Contract

## Objective

Define the provider and capability authorization surface used by Policy Fabric semantic validation and release-pack assembly.

## Why this exists

The authored policy contract already names `transform.provider` and `transform.capabilityRef`, but that information was previously validated only structurally. The capability catalog turns provider/capability authorization into a governed repository artifact.

## Current contract surfaces

- `contracts/policy_fabric_capability_catalog_v1.schema.json`
- `examples/policy_fabric_capability_catalog_example.json`
- `examples/policy_fabric_release_pack_example.json` now carries `spec.capabilityCatalog`

## What the current validator enforces

- provider ids are unique
- capability ids are unique
- every capability provider resolves to a declared provider
- capability transform types are allowed by the referenced provider
- approved policy rollout tenants and regions stay within the provider and capability allow-lists
- policy rules may only reference authorized provider/capability pairs

## Non-goal

This catalog is not yet a dynamic runtime registry. It is a governed repo artifact used for design-time semantic validation and release-pack integrity.
