# Release Snapshot

This export is the current cumulative Policy Fabric working repository snapshot.

## Snapshot notes

- repository governance is now enforced through managed ownership, workflow profiles, reconcile, and doctor
- authored-policy semantics are now checked against a governed capability catalog
- release packs now pin the capability catalog as part of the promotion boundary
- inspect `.git` inside the snapshot for exact commit history and final HEAD
- inspect `docs/reports/validation_report_latest.json` for the machine-readable validation evidence
