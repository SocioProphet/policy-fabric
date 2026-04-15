# Companion Placement Assessment v0

## Purpose

This assessment explains where companion-tranche material belongs relative to Policy Fabric.

## Placement model

### Belongs directly in Policy Fabric
Artifacts that are directly required for:
- governed promotion decisions
- downstream execution eligibility
- audit and explanation surfaces
- release gating
- stable operator-facing control outputs

### May stay upstream or external
Artifacts that are primarily:
- exploratory
- tranche-local
- threshold-sweep specific
- comparison-heavy without direct downstream execution value
- implementation scaffolding rather than governed control outputs

## Current recommendation

The narrow public-facing merge path should prefer:
- verdict report contract surfaces
- companion-policy binding notes
- placement assessments

and should avoid prematurely promoting richer tranche-local material that would make the public repository harder to reason about.

## Why this is the safe public posture

A public control repository should optimize for:
- legibility
- governed downstream usefulness
- stable semantics
- neutral public-facing naming

## Maintainer takeaway

When a companion tranche produces many possible artifacts, ask:
1. Is it downstream-consumable?
2. Is it central to governed execution or promotion?
3. Is it public-repo appropriate?
4. Is there a narrower artifact that captures the same decision value?

If the answer to (4) is yes, promote the narrower artifact first.
