# Agent Harness Policy Gate Model

Status: v0.1 planning baseline  
Owner plane: Policy Fabric / Guardrail Fabric  
Runtime producer: AgentPlane  
Metrics consumer: Delivery Excellence

## Purpose

Aden/Hive is useful because it normalizes generated agent graphs, judges, human-in-the-loop checks, skills, MCP tools, browser actions, failure diagnosis, and graph evolution. Policy Fabric should absorb the control pattern while making it stricter: every graph, tool grant, skill grant, MCP server, browser action, terminal action, model route, memory mount, human approval, and promotion event must be policy-checkable and evidence-linked.

This document defines the policy gate vocabulary needed for the cross-estate agent harness operating model.

## Boundary

Policy Fabric owns:

- policy contracts and compiled plans
- admission and promotion gates
- deterministic guardrail checks
- judge/eval policy structure
- human-control event requirements
- grant semantics for tools, skills, MCP servers, browser, terminal, memory, secrets, and network
- policy-sensitive evidence requirements

Policy Fabric does not own:

- runtime graph execution; AgentPlane owns it
- KPI/OKR scoreboards; Delivery Excellence owns them
- workspace topology; SocioSphere owns it
- security exercise execution; SCOPE-D owns it
- browser/terminal implementation; BearBrowser, TurtleTerm, and agent-term own it

## Gate family

### OutcomeAdmissionGate

Evaluates whether an `OutcomeSpec` is allowed to proceed toward planning.

Checks:

- legal/safety boundary
- owner/stakeholder present
- success criteria present
- risk tier assigned
- evidence requirements present
- budget/time boundaries present
- customer-sensitive data classification assigned

### PlanGraphReviewGate

Evaluates a user-reviewable plan graph before compilation into an executable graph.

Checks:

- every node has an owner and purpose
- assumptions are explicit
- human approvals are placed before risky actions
- policy gates precede live side effects
- no hidden credential or network dependency
- no unbounded loops
- expected evidence is declared

### GraphAdmissionGate

Evaluates executable `GraphSpec`.

Checks:

- node types are allowed
- edge types are allowed
- loop/retry bounds exist
- failure and escalation paths exist
- all tools/skills/MCP servers are grant-backed
- browser and terminal nodes have receipt requirements
- judge nodes have rubrics and confidence thresholds
- live mutation nodes require approval policy

### RunAdmissionGate

Evaluates `RunSpec` before execution.

Checks:

- executor class allowed
- model profile allowed
- network profile allowed
- filesystem scope allowed
- secret scope allowed
- memory mount allowed
- cost/time/tool-call caps present
- dry-run/live-run mode consistent with risk tier
- human approval requirement present when needed

### ToolGrantGate

Evaluates ordinary tool use.

Required grant fields:

- tool namespace
- operation
- allowed inputs
- allowed outputs
- side-effect class
- evidence requirement
- revocation behavior

### SkillGrantGate

Evaluates Agent Skills / `SKILL.md` activation.

Checks:

- trust tier
- signature/provenance if available
- allowed scripts/assets/references
- filesystem and network behavior
- prompt-injection risk note
- evals present for verified/official tiers
- SCOPE-D risk score when available

### MCPGrantGate

Evaluates MCP server and tool use.

Checks:

- registry entry present
- version pinned
- transport allowed
- tool schemas known
- credential needs declared
- namespace collision checked
- network/filesystem behavior declared
- health check passed
- SCOPE-D risk score when available

### BrowserActionGate

Evaluates BearBrowser/governed browser actions.

Risk actions requiring approval unless pre-granted:

- login or credential use
- form submit
- purchase/order/ticket creation
- download or upload
- account setting change
- external message send
- hidden/stealth automation mode

Required evidence:

- URL/domain
- action class
- screenshot or DOM/action receipt
- credential-use event when applicable
- download/upload manifest when applicable
- policy decision ref

### TerminalActionGate

Evaluates TurtleTerm/agent-term command execution.

Risk actions requiring approval unless pre-granted:

- package install
- filesystem mutation outside workspace
- network service start
- credential or key material access
- deployment/apply operation
- destructive command
- privilege escalation

Required evidence:

- command receipt
- working directory
- environment profile
- exit status
- stdout/stderr pointer
- artifact diff or mutation receipt
- policy decision ref

### MemoryGate

Evaluates Memory Mesh recall/writeback.

Checks:

- memory profile admitted
- sensitive payload storage posture
- recall scope allowed
- writeback scope allowed
- retention class assigned
- artifact pointer hash present for large/controlled payloads
- deletion/redaction semantics declared

### JudgeGate

Evaluates LLM or deterministic judge use.

Required fields:

- judge type: deterministic, LLM, hybrid, human
- rubric or rule ref
- confidence threshold
- appeal/escalation path
- evidence refs
- known limitations

### HumanControlGate

Ensures human intervention is recorded as a control event, not freeform hidden state.

Event types:

- approval
- rejection
- override
- clarification
- risk acceptance
- credential grant
- scope change
- promotion approval

### PromotionGate

Evaluates whether an agent graph, skill, MCP pack, template, policy, model profile, or runtime bundle can move to a higher trust state.

Checks:

- validation passed
- replay/simulation passed where available
- policy gate passed
- SCOPE-D/security result present for risky assets
- Delivery Excellence scoreboard impact known
- rollback/reversal path present
- human approval present when required

## Delivery Excellence integration

Policy Fabric should emit policy decisions and validation reports that can be projected into Delivery Excellence records:

- `DeliveryMetricEvent` for gate pass/fail, exception count, approval latency, blocked-run count, and promotion readiness
- `HumanControlEvent` for human approvals, overrides, risk acceptances, and credential grants
- `ScoreboardSnapshot` inputs for governance and safety/security scoreboards
- `CustomerProofReadout` evidence for policy-safe disclosure of what was approved and why

## Non-negotiables

- Generated graphs are denied until admitted.
- Live side effects are denied until explicitly granted.
- Browser and terminal side effects require receipts.
- Skills and MCP servers are treated as executable capability surfaces, not documentation.
- Human approvals are typed control events.
- Promotion requires evidence, not logs alone.
- Delivery scoreboards consume policy evidence but do not become policy authority.

## Next implementation tranche

1. Add JSON schemas for `AgentHarnessPolicyGateReport`, `SkillGrantDecision`, `MCPGrantDecision`, `BrowserActionDecision`, `TerminalActionDecision`, `HumanControlDecision`, and `PromotionGateDecision`.
2. Add example fixtures and validation.
3. Add Policy Fabric export projection to Delivery Excellence metric events.
4. Add SCOPE-D risk-score references for skills, MCP servers, browser actions, memory writes, and graph robustness.
