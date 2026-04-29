# Professional Intelligence Policy and Obligation Integration

## Purpose

This document defines the Policy Fabric role in Professional Intelligence OS.

Policy Fabric does not own contracts, workspace UX, model routing, or platform deployment. It owns policy authoring, compilation, validation, review, release packaging, replay evidence, and runtime policy decision semantics.

## Integration stance

Professional Intelligence OS needs policy enforcement at every boundary where institutional data, agents, tools, workspaces, contracts, or users interact.

Policy Fabric provides the policy-as-code layer for:

- data protection rules;
- AI-use restrictions;
- information barrier decisions;
- tool-use authorization;
- memory recall/writeback constraints;
- workspace access constraints;
- evidence retention constraints;
- release and promotion gates;
- policy replay and validation reports.

## Relationship to ContractForge

ContractForge owns contract lifecycle and obligation semantics. Policy Fabric owns executable policy overlays derived from those obligations.

Example split:

- ContractForge records that a client guideline prohibits use of generated summaries on confidential documents without approval.
- Policy Fabric compiles that obligation into a policy decision rule that blocks or escalates relevant agent/tool flows.
- Prophet Platform evaluates the policy before retrieval, tool execution, memory writeback, or output release.
- Model Governance Ledger and the platform Evidence Plane record the decision and replay inputs.

## Runtime decision points

Professional Intelligence OS must call Policy Fabric before:

1. retrieving restricted workspace documents;
2. exposing memory to an agent;
3. invoking a tool with side effects;
4. routing a prompt to a hosted model;
5. creating a workroom for a sensitive matter/deal/project;
6. releasing an agent-generated memo or packet;
7. bypassing or changing an information barrier;
8. approving a workflow stage with contractual or regulatory consequences.

## Policy decision receipt

Every runtime policy decision should produce or reference a receipt with:

- policy id and version;
- input subject, action, resource, and context;
- decision result: allow, deny, escalate, or require approval;
- obligation ids considered;
- wall or workspace boundary considered;
- model/tool routing constraints;
- evidence hash;
- replay pointer;
- human override, if any.

## Required policy families

Initial Professional Intelligence OS policy families:

- `ai-use-restriction`
- `information-barrier`
- `workspace-access`
- `memory-recall`
- `tool-grant`
- `model-routing`
- `contract-obligation-enforcement`
- `conflict-review-routing`
- `adoption-telemetry-retention`
- `evidence-retention`

## DelEx acceptance hooks

A Professional Intelligence OS playbook is not demo-acceptable unless policy evidence exists for every material governed step.

DelEx should reject demo acceptance if:

- a governed agent step has no policy decision;
- a sensitive workspace action has no access check;
- a contract-derived obligation has no policy mapping;
- a human override exists without explanation;
- replay evidence is missing or incomplete.

## Near-term implementation targets

1. Add a `ProfessionalPolicyDecision` schema or extend the existing broker policy decision contract for professional workflows.
2. Add examples for AI-use restriction, information barrier, tool grant, model routing, and contract-obligation enforcement.
3. Add validation that every playbook step marked `evidenceRequired: true` has a policy or evidence path.
4. Publish release-pack examples consumed by `prophet-platform` runtime smoke tests.
