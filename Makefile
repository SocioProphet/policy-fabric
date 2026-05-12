.PHONY: validate operations-decision-smoke operations-decision-api-smoke product-suite-policy-validate model-fabric-release-policy-validate lattice-data-governai-policy-subjects-validate lattice-data-governai-expanded-policy-subjects-validate lattice-runtime-profile-policy-subjects-validate lattice-runtime-promotion-policy-validate diff-hygiene-gate-validate agent-reliability-overrides-validate prophet-understand-smoke semantic-enterprise-policy-input-validate ops-history-policy-validate sourceos-capability-decision-policy-validate policy-fabric-cancellation-binding-tier2-binding-ci

validate: operations-decision-smoke operations-decision-api-smoke product-suite-policy-validate model-fabric-release-policy-validate lattice-data-governai-policy-subjects-validate lattice-data-governai-expanded-policy-subjects-validate lattice-runtime-profile-policy-subjects-validate lattice-runtime-promotion-policy-validate diff-hygiene-gate-validate agent-reliability-overrides-validate prophet-understand-smoke semantic-enterprise-policy-input-validate ops-history-policy-validate sourceos-capability-decision-policy-validate policy-fabric-cancellation-binding-tier2-binding-ci
	@echo "OK: validate"

operations-decision-smoke:
	python3 -m pip install --user jsonschema >/dev/null
	python3 tools/smoke_operations_decision_service.py

operations-decision-api-smoke:
	python3 -m pip install --user jsonschema fastapi >/dev/null
	python3 tools/smoke_operations_decision_api.py

product-suite-policy-validate:
	python3 tools/validate_product_suite_policy.py

model-fabric-release-policy-validate:
	python3 tools/validate_model_fabric_release_policy.py

lattice-data-governai-policy-subjects-validate:
	python3 tools/validate_lattice_data_governai_policy_subjects.py

lattice-data-governai-expanded-policy-subjects-validate:
	python3 tools/validate_lattice_data_governai_expanded_policy_subjects.py

lattice-runtime-profile-policy-subjects-validate:
	python3 tools/validate_lattice_runtime_profile_policy_subjects.py

lattice-runtime-promotion-policy-validate:
	python3 tools/validate_lattice_runtime_promotion_policy.py

diff-hygiene-gate-validate:
	python3 tools/validate_diff_hygiene_gate.py

agent-reliability-overrides-validate:
	python3 tools/validate_agent_reliability_overrides.py

prophet-understand-smoke:
	python3 tools/smoke_prophet_understand_policy.py

semantic-enterprise-policy-input-validate:
	python3 tools/validate_semantic_enterprise_policy_input.py

ops-history-policy-validate:
	python3 tools/validate_ops_history_policy_examples.py

sourceos-capability-decision-policy-validate:
	python3 tools/validate_sourceos_capability_decision_policy.py

policy-fabric-cancellation-binding-tier2-binding-ci:
	python3 -m json.tool schemas/composition/policy-fabric-cancellation-binding-tier2-binding.v1.json >/dev/null
	python3 -m json.tool tests/fixtures/composition/policy-fabric-cancellation-binding-tier2-binding.synthetic.json >/dev/null
	python3 -m json.tool tests/fixtures/composition/policy-fabric-cancellation-binding-tier2-binding.runtime-field.invalid.synthetic.json >/dev/null
	python3 tools/check_policy_fabric_cancellation_binding_tier2_binding.py tests/fixtures/composition/policy-fabric-cancellation-binding-tier2-binding.synthetic.json
	! python3 tools/check_policy_fabric_cancellation_binding_tier2_binding.py tests/fixtures/composition/policy-fabric-cancellation-binding-tier2-binding.runtime-field.invalid.synthetic.json
