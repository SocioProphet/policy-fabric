# Security Policy

## Supported versions

Policy Fabric is currently under active development.

We currently support security reports against:

| Version / Branch | Supported |
| --- | --- |
| `main` | Yes |
| active release candidate branches explicitly called out by maintainers | Case-by-case |
| historical work branches | No |

## Reporting a vulnerability

Please do **not** open a public GitHub issue for suspected vulnerabilities.

Use one of these channels instead:

1. Preferred: GitHub private vulnerability reporting / security advisory flow, if enabled for this repository.
2. Fallback: email `michael@socioprophet.ai` with the subject line `Policy Fabric security report`.

If you later establish a dedicated security inbox, replace the fallback address above with that inbox.

## What to include

Please include as much of the following as possible:

- affected branch, commit, or tag
- steps to reproduce
- impacted contract, validator, workflow, or report surface
- expected behavior vs actual behavior
- severity or impact assessment
- proof-of-concept or minimal reproducer, if safe to share

## Response expectations

We aim to:

- acknowledge receipt within 5 business days
- determine whether the report is reproducible and in scope
- coordinate a fix and disclosure path where appropriate

## Disclosure guidance

Please give us reasonable time to validate and remediate before public disclosure.

If the issue affects generated examples or reports rather than executable behavior, still report it if it could mislead operators or weaken security posture.
