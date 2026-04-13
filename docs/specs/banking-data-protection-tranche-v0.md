# Banking Data-Protection Tranche v0.1

## Purpose

This tranche stages the first **banking-twin-aligned Policy Fabric artifacts**.

Important boundary:
the current Policy Fabric contract surface is primarily a governed **data-protection policy**
surface built around selectors, transform rules, rollout, fixtures, release packs,
validation reports, and replay reports.

Therefore, this tranche focuses on policy where that contract is a clean fit:

- filing publication masking
- counterparty export tokenization
- operator note redaction for review and audit workflows

It does **not** yet attempt to force generic model-promotion or approval-state semantics
into the v2 policy contract.

## Tranche contents

- banking filing publication policy example
- banking counterparty export policy example
- banking operator review-note redaction policy example
- boundary note describing fit and non-fit with current Policy Fabric contracts

## Why this order

Banking twin work needs governance depth, but the governance surface should match the
actual repository contracts. This tranche establishes that fit honestly before any
broader approval/governance pack is proposed.

## Planned next step

- decide whether broader approval semantics should:
  1. extend Policy Fabric with a new contract family, or
  2. remain in a sibling governance repo while Policy Fabric handles protection policy.
