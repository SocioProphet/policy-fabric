# AgentPlane no-touch compatibility probe — 2026-04-02

## Purpose

Move beyond planning and perform the first real compatibility probe against the official AgentPlane workflow model without hand-authoring a fake `.agentplane/` tree in the authoritative repository.

## What we tested

- local prerequisites in the disposable clone environment
- current Policy Fabric surface collisions against the official documented init surface
- whether we could execute the public CLI package path from this container

## What we observed

- Node.js and npm are available locally in the container.
- The repository already contains `AGENTS.md`, which is the main collision point with official AgentPlane.
- The repository does **not** yet contain a `.agentplane/` tree, so there is no mixed-state or partial-upgrade condition.
- The repository already has a rich product-specific workflow surface under `.policy-fabric/`.
- Package metadata for the public `agentplane` package is discoverable from npm in this environment, but package execution through `npx -y agentplane --help` failed with an authentication error in the container npm execution path.

## What this means

We have enough evidence to define the bridge contract and to know where the real collisions are.
We do **not** yet have a trustworthy basis to claim that official `agentplane init` has been executed against this repo.
That remains future work for an environment where the CLI can actually be run cleanly.

## Result

The right near-term outcome is a hybrid bridge model:

- keep `.policy-fabric/` authoritative for Policy Fabric governance and product validation;
- prepare for official AgentPlane to own `.agentplane/` once real initialization is executed on a dedicated branch;
- continue to treat `AGENTS.md` as the shared root gateway that will need intentional reconciliation.
