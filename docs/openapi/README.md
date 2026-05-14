# OpenAPI stubs

This directory contains review stubs for API surfaces whose full machine contract is tracked separately.

## Constitutional Policy Engine v0.1

File: `constitutional-policy-engine-v0_1.stub.yaml`

Purpose:

- expose the reviewable endpoint shape for A1, A3, A4, A5, and A7;
- align response fields with the current Python reference dataclasses;
- avoid claiming deployed API status before the service wrapper exists;
- keep the full OpenAPI upload as an explicit follow-up artifact.

The stub is intentionally not the final deployed API contract. Missing from this tranche:

- complete error response shapes;
- final request and response validation constraints;
- `/verdict` solver-backed semantics;
- HTTP framework binding;
- schema registry host selection;
- audit-log substrate selection.

Follow-up issue/PR should materialize the exact OpenAPI 3.1 source drop once the connector upload path is unblocked.
