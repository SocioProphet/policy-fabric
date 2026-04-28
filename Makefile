.PHONY: validate operations-decision-smoke operations-decision-api-smoke product-suite-policy-validate

validate: operations-decision-smoke operations-decision-api-smoke product-suite-policy-validate
	@echo "OK: validate"

operations-decision-smoke:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/smoke_operations_decision_service.py

operations-decision-api-smoke:
	python3 -m pip install --user jsonschema fastapi >/dev/null
	python3 tools/smoke_operations_decision_api.py

product-suite-policy-validate:
	python3 tools/validate_product_suite_policy.py
