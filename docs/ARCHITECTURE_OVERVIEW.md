# Architecture Overview

Policy Fabric is a governed control repository for policy, validation, promotion, and evidence.

## System model

Policy Fabric is organized in five layers.

### 1. Authored policy layer
Human-authored policy defines selectors, rules, rollout scope, provider/capability references, and fixtures.

Primary surfaces:
- contracts/policy_fabric_policy_v2.schema.json
- examples/policy_fabric_policy_v2_enhanced_example.json

### 2. Compiled execution layer
Compiled plans translate authored policy into deterministic, execution-oriented structure.

Primary surfaces:
- contracts/policy_fabric_execution_plan_ir_v1.schema.json
- examples/policy_fabric_compiled_plan_example.json

### 3. Promotion and evidence layer
Release packs, validation reports, and replay reports bind policy to review, evidence, and promotion semantics.

Primary surfaces:
- contracts/policy_fabric_release_pack_v1.schema.json
- contracts/policy_fabric_validation_report_v1.schema.json
- contracts/policy_fabric_replay_report_v1.schema.json
- examples/policy_fabric_release_pack_example.json
- examples/policy_fabric_validation_report_example.json
- examples/policy_fabric_replay_report_example.json

### 4. Governance layer
The .policy-fabric directory defines:
- ownership classification
- workflow profile and branch policy
- publish expectations
- AgentPlane bridge expectations

### 5. Workflow layer
The .agentplane directory is the official AgentPlane workflow surface integrated around the repository.

Policy Fabric governance remains authoritative for product semantics. AgentPlane governs repo-native workflow surfaces and local task/runtime structure.

## Standard repository loop

Run:
- python3 scripts/reconcile.py
- python3 scripts/doctor.py

When workflow or governance surfaces changed, also run:
- python3 scripts/agentplane_probe.py
- python3 scripts/branch_audit.py
- python3 scripts/github_publish_prep.py

## Review principle

Contracts, examples, reports, and governance surfaces are first-class review material in this repository.
