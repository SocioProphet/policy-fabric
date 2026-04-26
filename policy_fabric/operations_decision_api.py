from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .operations_decision_service import evaluate_operations_action

app = FastAPI(title="policy-fabric-operations-decision", version="0.1.0")


class OperationsDecisionRequest(BaseModel):
    recommendation: dict[str, Any] = Field(default_factory=dict)
    mode: str = "report_only"


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "policy-fabric-operations-decision"}


@app.post("/v1/operations/action-decision")
def operations_action_decision(body: OperationsDecisionRequest) -> dict[str, Any]:
    return evaluate_operations_action(body.recommendation, mode=body.mode)
