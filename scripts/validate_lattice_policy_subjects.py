#!/usr/bin/env python3
"""Validate Policy Fabric Lattice platform asset policy-subject fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(path: Path) -> None:
    doc = json.loads(path.read_text(encoding="utf-8"))
    require(doc.get("apiVersion") == "policy-fabric.socioprophet.dev/v1", "apiVersion mismatch")
    require(doc.get("kind") == "PolicySubjectFixture", "kind mismatch")
    subject = doc.get("subject")
    require(isinstance(subject, dict), "subject must be an object")
    require(subject.get("sourceRecordKind") == "PlatformAssetRecord", "sourceRecordKind mismatch")
    require(isinstance(subject.get("assetId"), str) and subject["assetId"], "assetId is required")
    require(isinstance(subject.get("policySubjectClass"), str) and subject["policySubjectClass"], "policySubjectClass is required")
    require(isinstance(subject.get("compatibilitySurfaces"), list), "compatibilitySurfaces must be a list")
    require(isinstance(doc.get("policyQuestions"), list) and doc["policyQuestions"], "policyQuestions must be non-empty")
    require(isinstance(doc.get("expectedGateStatus"), str) and doc["expectedGateStatus"], "expectedGateStatus is required")


def main(argv: list[str] | None = None) -> int:
    paths = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not paths:
        paths = sorted(Path("examples/lattice").glob("*.json"))
    failed = False
    for path in paths:
        try:
            validate(path)
            print(f"PASS {path}")
        except Exception as exc:  # noqa: BLE001
            failed = True
            print(f"FAIL {path}: {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
