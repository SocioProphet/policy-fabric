.PHONY: validate operations-decision-smoke

validate: operations-decision-smoke
	@echo "OK: validate"

operations-decision-smoke:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/smoke_operations_decision_service.py
