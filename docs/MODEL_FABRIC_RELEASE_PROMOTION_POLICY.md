# Model Fabric Release Promotion Policy

This policy pack defines the gates required before model-fabric tools move from development-source formulae to stable immutable release-artifact formulae.

## Ownership

`policy-fabric` owns the promotion policy. `homebrew-prophet` owns formula templates and generated formulae. Individual tool repositories own their release dry-run manifests and release artifacts. `model-governance-ledger` owns promotion and rollback evidence records. SourceOS remains carry-only and does not own mutable model lifecycle authority.

## Development formulae

Development formulae and local dry-run artifacts are allowed for CI, local validation, and integration testing. They must not claim stable release readiness, production certification, or Homebrew installability unless immutable release inputs exist.

Development artifacts may reference Git refs, local `dist/` outputs, and dry-run manifests. They may not invent stable release URLs or checksums.

## Stable release artifact formulae

A stable release artifact formula requires all promotion gates:

- release dry-run;
- versioned GitHub Release;
- immutable artifact URL;
- SHA-256 checksum;
- SBOM reference;
- provenance reference;
- Homebrew formula test evidence;
- SourceOS carry-only boundary check.

Placeholders are allowed only in templates or documentation paths such as `Formula/templates/`, `templates/`, or `docs/`. Active formulae must not contain fake URLs, fake checksums, or placeholder values.

## Evidence requirements

Each promotion must carry references for the dry-run manifest, release tag, artifact URL, artifact SHA-256, SBOM, provenance, formula test evidence, and ledger promotion record.

Readiness scores are not certification. They are advisory evidence used to decide whether promotion is blocked, ready for review, or ready for release.
