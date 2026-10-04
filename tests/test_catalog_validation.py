from __future__ import annotations

import copy
import json
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from scripts.validation import (
    CatalogKind,
    CatalogLifecyclePolicy,
    CatalogRegistry,
    CatalogRegistryError,
    DuplicateCatalogIdError,
    EosValidator,
    ValidationContext,
)


ROOT = Path(__file__).resolve().parents[1]
CONTEXT_FIXTURE = ROOT / "tests" / "fixtures" / "catalog-context" / "fictional-catalog-context.json"

QUANTITY_SCHEMA = "https://eos.local/schemas/knowledge-core/quantity.schema.json"
VALUE_RANGE_SCHEMA = "https://eos.local/schemas/knowledge-core/value-range.schema.json"
MEASUREMENT_QUALITY_SCHEMA = "https://eos.local/schemas/knowledge-core/measurement-quality.schema.json"
CONDITION_SCHEMA = "https://eos.local/schemas/knowledge-core/condition.schema.json"
CLASSIFICATION_SCHEMA = "https://eos.local/schemas/knowledge-core/classification.schema.json"
PROPERTY_RECORD_SCHEMA = "https://eos.local/schemas/knowledge-core/property-record.schema.json"
OBSERVATION_SCHEMA = "https://eos.local/schemas/knowledge-core/observation.schema.json"
INDEX_SCHEMA = "https://eos.local/schemas/index.schema.json"

CATALOG_SCHEMAS = {
    "unitEntries": "https://eos.local/schemas/catalogs/unit-catalog-entry.schema.json",
    "conditionTypeEntries": "https://eos.local/schemas/catalogs/condition-type-catalog-entry.schema.json",
    "propertyEntries": "https://eos.local/schemas/catalogs/property-catalog-entry.schema.json",
    "classificationEntries": "https://eos.local/schemas/catalogs/classification-catalog-entry.schema.json",
}


def load_catalog_data() -> dict:
    with CONTEXT_FIXTURE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_registry(data: dict | None = None) -> CatalogRegistry:
    source = data or load_catalog_data()
    return CatalogRegistry(
        unit_entries=source["unitEntries"],
        condition_type_entries=source["conditionTypeEntries"],
        property_entries=source["propertyEntries"],
        classification_entries=source["classificationEntries"],
    )


def quantity(unit_id: str = "UNT-980001") -> dict:
    return {"value": 1, "unitId": unit_id}


def value_range(unit_id: str = "UNT-980001") -> dict:
    return {"minValue": 1, "maxValue": 2, "unitId": unit_id}


def condition(
    condition_type_id: str = "CND-980001",
    *,
    field: str = "quantity",
    value: object | None = None,
) -> dict:
    defaults = {
        "quantity": quantity(),
        "valueRange": value_range(),
        "textValue": "fictional test value",
        "booleanValue": True,
        "referenceId": "MAT-9801",
    }
    return {
        "conditionTypeId": condition_type_id,
        "evaluationMode": "contextual",
        field: defaults[field] if value is None else value,
    }


def property_record(
    property_id: str = "PRP-980001",
    *,
    value_type: str = "quantity",
    unit_id: str = "UNT-980001",
    conditions: list[dict] | None = None,
) -> dict:
    record = {
        "propertyId": property_id,
        "valueType": value_type,
        value_type: quantity(unit_id) if value_type == "quantity" else value_range(unit_id),
        "verificationStatus": "Draft",
        "sourceLinks": [],
    }
    if conditions is not None:
        record["conditions"] = conditions
    return record


def observation(
    property_id: str = "PRP-980001",
    *,
    value_type: str = "quantity",
    unit_id: str = "UNT-980001",
    conditions: list[dict] | None = None,
) -> dict:
    record = {
        "id": "OBS-980001",
        "schemaVersion": "0.1.0",
        "recordVersion": "0.1.0",
        "revision": 0,
        "status": "Draft",
        "createdAt": "2026-01-01T00:01:00Z",
        "createdBy": "test-suite",
        "updatedAt": "2026-01-01T00:01:00Z",
        "updatedBy": "test-suite",
        "sourceLinks": [],
        "changeSummary": "Initial fictional test observation.",
        "subjectId": "MAT-9801",
        "observationScope": "GLOBAL",
        "observedAt": "2026-01-01T00:00:00Z",
        "propertyId": property_id,
        "valueType": value_type,
        value_type: quantity(unit_id) if value_type == "quantity" else value_range(unit_id),
    }
    if conditions is not None:
        record["conditions"] = conditions
    return record


class CatalogRegistryTests(unittest.TestCase):
    def test_fictional_entries_pass_their_contracts_before_registration(self) -> None:
        validator = EosValidator()
        data = load_catalog_data()
        for family, schema_id in CATALOG_SCHEMAS.items():
            for entry in data[family]:
                with self.subTest(entry=entry["id"]):
                    result = validator.validate(entry, schema_id)
                    self.assertTrue(result.ok, [(error.path, error.message) for error in result.errors])

    def test_registry_constructs_all_four_typed_catalogs(self) -> None:
        registry = build_registry()
        self.assertEqual(len(registry), 15)
        self.assertEqual(registry.resolve("UNT-980001").kind, CatalogKind.UNIT)
        self.assertEqual(registry.resolve("CND-980001").kind, CatalogKind.CONDITION_TYPE)
        self.assertEqual(registry.resolve("PRP-980001").kind, CatalogKind.PROPERTY)
        self.assertEqual(registry.resolve("CLS-980001").kind, CatalogKind.CLASSIFICATION)

    def test_registry_returns_none_for_missing_reference(self) -> None:
        self.assertIsNone(build_registry().resolve("UNT-999999"))

    def test_duplicate_ids_fail_closed_for_each_catalog_family(self) -> None:
        source_keys = (
            "unitEntries",
            "conditionTypeEntries",
            "propertyEntries",
            "classificationEntries",
        )
        for source_key in source_keys:
            with self.subTest(catalog=source_key):
                data = load_catalog_data()
                data[source_key].append(copy.deepcopy(data[source_key][0]))
                with self.assertRaises(DuplicateCatalogIdError) as caught:
                    build_registry(data)
                self.assertEqual(caught.exception.error_code, "reference_integrity.duplicate_catalog_id")

    def test_wrong_catalog_family_registration_fails_closed(self) -> None:
        property_entry = load_catalog_data()["propertyEntries"][0]
        with self.assertRaises(CatalogRegistryError) as caught:
            CatalogRegistry(unit_entries=[property_entry])
        self.assertEqual(caught.exception.error_code, "reference_integrity.catalog_entry_type_mismatch")

    def test_registry_and_context_are_immutable(self) -> None:
        registry = build_registry()
        context = ValidationContext(registry)
        with self.assertRaises(TypeError):
            registry.unit_entries["UNT-980099"] = {}  # type: ignore[index]
        with self.assertRaises(TypeError):
            registry.unit_entries["UNT-980001"]["name"] = "changed"  # type: ignore[index]
        with self.assertRaises(TypeError):
            registry.property_entries["PRP-980001"]["allowedUnitIds"] += ("UNT-980002",)  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            context.lifecycle_policy = CatalogLifecyclePolicy.AUTHORING  # type: ignore[misc]


class CatalogAwareValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = EosValidator()
        self.registry = build_registry()
        self.context = ValidationContext(self.registry)
        self.authoring_context = ValidationContext(
            self.registry,
            lifecycle_policy=CatalogLifecyclePolicy.AUTHORING,
        )

    def assertError(
        self,
        result,
        code: str,
        path: str | None = None,
        *,
        category: str | None = None,
    ) -> None:
        matches = [error for error in result.errors if error.errorCode == code]
        self.assertTrue(matches, [(error.errorCode, error.path) for error in result.errors])
        if path is not None:
            self.assertIn(path, [error.path for error in matches])
        if category is not None:
            self.assertTrue(all(error.category == category for error in matches))

    def assertNoError(self, result, code: str) -> None:
        self.assertNotIn(code, [error.errorCode for error in result.errors])

    def test_contract_only_validation_remains_backward_compatible(self) -> None:
        result = self.validator.validate(quantity("UNT-999999"), QUANTITY_SCHEMA)
        self.assertTrue(result.ok)
        self.assertEqual(result.executedLayers, ("schema_validation", "application_validation"))

    def test_context_aware_validation_requires_explicit_context(self) -> None:
        result = self.validator.validate_with_context(quantity(), QUANTITY_SCHEMA, None)
        self.assertFalse(result.ok)
        self.assertError(result, "catalog_validation.context_required", "$", category="catalog_validation")

    def test_context_aware_file_validation_reports_json_syntax_layer(self) -> None:
        fixture = ROOT / "tests" / "fixtures" / "valid" / "knowledge-core" / "quantity-decimal-valid.json"
        result = self.validator.validate_json_file_with_context(fixture, QUANTITY_SCHEMA, None)
        self.assertFalse(result.ok)
        self.assertEqual(result.executedLayers, ("json_syntax",))
        self.assertError(result, "catalog_validation.context_required", "$")

    def test_structural_failure_prevents_catalog_checks(self) -> None:
        record = property_record(property_id="PRP-invalid")
        result = self.validator.validate_with_context(record, PROPERTY_RECORD_SCHEMA, self.context)
        self.assertFalse(result.ok)
        self.assertIn("schema_validation", {error.category for error in result.errors})
        self.assertNotIn("reference_integrity", {error.category for error in result.errors})
        self.assertNotIn("catalog_validation", {error.category for error in result.errors})
        self.assertEqual(result.executedLayers, ("schema_validation", "application_validation"))

        malformed_unit = self.validator.validate_with_context(
            quantity("UNT-invalid"), QUANTITY_SCHEMA, self.context
        )
        self.assertIn("schema_validation", {error.category for error in malformed_unit.errors})
        self.assertNotIn("reference_integrity", {error.category for error in malformed_unit.errors})

    def test_quantity_unit_reference_exists_or_reports_missing(self) -> None:
        valid = self.validator.validate_with_context(quantity(), QUANTITY_SCHEMA, self.context)
        missing = self.validator.validate_with_context(quantity("UNT-999999"), QUANTITY_SCHEMA, self.context)
        self.assertTrue(valid.ok)
        self.assertEqual(
            valid.executedLayers,
            ("schema_validation", "application_validation", "reference_integrity", "catalog_validation"),
        )
        self.assertError(
            missing,
            "reference_integrity.reference_not_found",
            "$.unitId",
            category="reference_integrity",
        )

    def test_value_range_unit_reference_exists_or_reports_missing(self) -> None:
        self.assertTrue(
            self.validator.validate_with_context(value_range(), VALUE_RANGE_SCHEMA, self.context).ok
        )
        result = self.validator.validate_with_context(
            value_range("UNT-999999"), VALUE_RANGE_SCHEMA, self.context
        )
        self.assertError(result, "reference_integrity.reference_not_found", "$.unitId")

    def test_measurement_quality_reuses_nested_unit_validation(self) -> None:
        record = {
            "uncertainty": quantity(),
            "resolution": quantity("UNT-999999"),
        }
        result = self.validator.validate_with_context(
            record, MEASUREMENT_QUALITY_SCHEMA, self.context
        )
        self.assertError(
            result,
            "reference_integrity.reference_not_found",
            "$.resolution.unitId",
        )
        self.assertNotIn("$.uncertainty.unitId", [error.path for error in result.errors])

    def test_condition_allows_configured_quantity_and_text_forms(self) -> None:
        quantity_result = self.validator.validate_with_context(
            condition(), CONDITION_SCHEMA, self.context
        )
        text_result = self.validator.validate_with_context(
            condition("CND-980002", field="textValue"), CONDITION_SCHEMA, self.context
        )
        self.assertTrue(quantity_result.ok)
        self.assertTrue(text_result.ok)

    def test_missing_condition_type_suppresses_dependent_form_error(self) -> None:
        result = self.validator.validate_with_context(
            condition("CND-999999", field="textValue"), CONDITION_SCHEMA, self.context
        )
        self.assertError(
            result,
            "reference_integrity.reference_not_found",
            "$.conditionTypeId",
        )
        self.assertNoError(result, "catalog_validation.condition_value_form_not_allowed")

    def test_condition_rejects_disallowed_value_form(self) -> None:
        result = self.validator.validate_with_context(
            condition("CND-980001", field="textValue"), CONDITION_SCHEMA, self.context
        )
        self.assertError(
            result,
            "catalog_validation.condition_value_form_not_allowed",
            "$",
            category="catalog_validation",
        )

    def test_condition_reference_prefix_policy_is_catalog_aware(self) -> None:
        allowed = self.validator.validate_with_context(
            condition("CND-980003", field="referenceId", value="MAT-9801"),
            CONDITION_SCHEMA,
            self.context,
        )
        disallowed = self.validator.validate_with_context(
            condition("CND-980003", field="referenceId", value="MAC-9801"),
            CONDITION_SCHEMA,
            self.context,
        )
        self.assertTrue(allowed.ok)
        self.assertError(
            disallowed,
            "catalog_validation.reference_prefix_not_allowed",
            "$.referenceId",
        )

    def test_condition_reuses_nested_unit_reference_validation(self) -> None:
        quantity_result = self.validator.validate_with_context(
            condition(value=quantity("UNT-999999")), CONDITION_SCHEMA, self.context
        )
        range_result = self.validator.validate_with_context(
            condition(
                "CND-980004",
                field="valueRange",
                value=value_range("UNT-999999"),
            ),
            CONDITION_SCHEMA,
            self.context,
        )
        self.assertError(
            quantity_result,
            "reference_integrity.reference_not_found",
            "$.quantity.unitId",
        )
        self.assertError(
            range_result,
            "reference_integrity.reference_not_found",
            "$.valueRange.unitId",
        )

    def test_property_record_accepts_allowed_property_value_and_unit(self) -> None:
        result = self.validator.validate_with_context(
            property_record(), PROPERTY_RECORD_SCHEMA, self.context
        )
        self.assertTrue(result.ok, [(error.errorCode, error.path) for error in result.errors])

    def test_property_record_missing_property_suppresses_dependent_checks(self) -> None:
        result = self.validator.validate_with_context(
            property_record(
                property_id="PRP-999999",
                unit_id="UNT-980002",
                conditions=[condition()],
            ),
            PROPERTY_RECORD_SCHEMA,
            self.context,
        )
        self.assertError(result, "reference_integrity.reference_not_found", "$.propertyId")
        self.assertNoError(result, "catalog_validation.value_type_not_allowed")
        self.assertNoError(result, "catalog_validation.unit_not_allowed")
        self.assertNoError(result, "catalog_validation.condition_not_allowed")

    def test_property_record_rejects_disallowed_value_type(self) -> None:
        result = self.validator.validate_with_context(
            property_record(value_type="valueRange"), PROPERTY_RECORD_SCHEMA, self.context
        )
        self.assertError(result, "catalog_validation.value_type_not_allowed", "$.valueType")

    def test_property_record_distinguishes_missing_and_disallowed_units(self) -> None:
        missing = self.validator.validate_with_context(
            property_record(unit_id="UNT-999999"), PROPERTY_RECORD_SCHEMA, self.context
        )
        disallowed = self.validator.validate_with_context(
            property_record(unit_id="UNT-980002"), PROPERTY_RECORD_SCHEMA, self.context
        )
        self.assertError(missing, "reference_integrity.reference_not_found", "$.quantity.unitId")
        self.assertNoError(missing, "catalog_validation.unit_not_allowed")
        self.assertError(disallowed, "catalog_validation.unit_not_allowed", "$.quantity.unitId")
        self.assertNoError(disallowed, "reference_integrity.reference_not_found")

    def test_property_record_forbids_conditions_when_allowlist_is_absent(self) -> None:
        result = self.validator.validate_with_context(
            property_record(conditions=[condition()]), PROPERTY_RECORD_SCHEMA, self.context
        )
        self.assertError(
            result,
            "catalog_validation.condition_not_allowed",
            "$.conditions[0].conditionTypeId",
        )

    def test_property_record_accepts_listed_condition_and_rejects_unlisted_condition(self) -> None:
        allowed = self.validator.validate_with_context(
            property_record(
                property_id="PRP-980003",
                conditions=[condition("CND-980001")],
            ),
            PROPERTY_RECORD_SCHEMA,
            self.context,
        )
        disallowed = self.validator.validate_with_context(
            property_record(
                property_id="PRP-980003",
                conditions=[condition("CND-980004", field="valueRange")],
            ),
            PROPERTY_RECORD_SCHEMA,
            self.context,
        )
        self.assertTrue(allowed.ok)
        self.assertError(
            disallowed,
            "catalog_validation.condition_not_allowed",
            "$.conditions[0].conditionTypeId",
        )

    def test_property_record_nested_condition_rules_remain_independent(self) -> None:
        missing = self.validator.validate_with_context(
            property_record(
                property_id="PRP-980003",
                conditions=[condition("CND-999999", field="textValue")],
            ),
            PROPERTY_RECORD_SCHEMA,
            self.context,
        )
        wrong_form = self.validator.validate_with_context(
            property_record(
                property_id="PRP-980003",
                conditions=[condition("CND-980001", field="textValue")],
            ),
            PROPERTY_RECORD_SCHEMA,
            self.context,
        )
        self.assertError(missing, "reference_integrity.reference_not_found", "$.conditions[0].conditionTypeId")
        self.assertNoError(missing, "catalog_validation.condition_value_form_not_allowed")
        self.assertError(wrong_form, "catalog_validation.condition_value_form_not_allowed", "$.conditions[0]")

    def test_measurement_quality_unit_is_not_restricted_by_property_allowlist(self) -> None:
        record = property_record()
        record["measurementQuality"] = {"uncertainty": quantity("UNT-980002")}
        result = self.validator.validate_with_context(record, PROPERTY_RECORD_SCHEMA, self.context)
        self.assertTrue(result.ok, [(error.errorCode, error.path) for error in result.errors])

    def test_observation_reuses_property_compatibility(self) -> None:
        valid = self.validator.validate_with_context(observation(), OBSERVATION_SCHEMA, self.context)
        missing_property = self.validator.validate_with_context(
            observation(property_id="PRP-999999"), OBSERVATION_SCHEMA, self.context
        )
        disallowed_type = self.validator.validate_with_context(
            observation(value_type="valueRange"), OBSERVATION_SCHEMA, self.context
        )
        disallowed_unit = self.validator.validate_with_context(
            observation(unit_id="UNT-980002"), OBSERVATION_SCHEMA, self.context
        )
        self.assertTrue(valid.ok)
        self.assertError(missing_property, "reference_integrity.reference_not_found", "$.propertyId")
        self.assertError(disallowed_type, "catalog_validation.value_type_not_allowed", "$.valueType")
        self.assertError(disallowed_unit, "catalog_validation.unit_not_allowed", "$.quantity.unitId")

    def test_observation_reuses_condition_allowlist(self) -> None:
        allowed = self.validator.validate_with_context(
            observation(
                property_id="PRP-980003",
                conditions=[condition("CND-980002", field="textValue")],
            ),
            OBSERVATION_SCHEMA,
            self.context,
        )
        disallowed = self.validator.validate_with_context(
            observation(
                property_id="PRP-980003",
                conditions=[condition("CND-980004", field="valueRange")],
            ),
            OBSERVATION_SCHEMA,
            self.context,
        )
        self.assertTrue(allowed.ok)
        self.assertError(
            disallowed,
            "catalog_validation.condition_not_allowed",
            "$.conditions[0].conditionTypeId",
        )

    def test_classification_resolves_and_obeys_lifecycle(self) -> None:
        approved = self.validator.validate_with_context(
            {"classificationId": "CLS-980001"}, CLASSIFICATION_SCHEMA, self.context
        )
        missing = self.validator.validate_with_context(
            {"classificationId": "CLS-999999"}, CLASSIFICATION_SCHEMA, self.context
        )
        draft = self.validator.validate_with_context(
            {"classificationId": "CLS-980002"}, CLASSIFICATION_SCHEMA, self.context
        )
        self.assertTrue(approved.ok)
        self.assertError(missing, "reference_integrity.reference_not_found", "$.classificationId")
        self.assertError(draft, "catalog_validation.catalog_status_not_allowed", "$.classificationId")

    def test_default_lifecycle_policy_handles_all_statuses(self) -> None:
        expectations = {
            "UNT-980001": (True, None),
            "UNT-980003": (False, "catalog_validation.catalog_status_not_allowed"),
            "UNT-980004": (False, "catalog_validation.catalog_status_not_allowed"),
            "UNT-980005": (True, "catalog_validation.deprecated_reference"),
            "UNT-980006": (False, "catalog_validation.catalog_status_not_allowed"),
        }
        for unit_id, (expected_ok, code) in expectations.items():
            with self.subTest(unit=unit_id):
                result = self.validator.validate_with_context(
                    quantity(unit_id), QUANTITY_SCHEMA, self.context
                )
                self.assertEqual(result.ok, expected_ok)
                if code:
                    self.assertError(result, code, "$.unitId")
        deprecated = self.validator.validate_with_context(
            quantity("UNT-980005"), QUANTITY_SCHEMA, self.context
        )
        self.assertEqual(len(deprecated.warnings), 1)
        self.assertEqual(deprecated.warnings[0].severity, "warning")

    def test_authoring_policy_allows_draft_and_review_but_not_archived(self) -> None:
        for unit_id in ("UNT-980003", "UNT-980004"):
            with self.subTest(unit=unit_id):
                result = self.validator.validate_with_context(
                    quantity(unit_id), QUANTITY_SCHEMA, self.authoring_context
                )
                self.assertTrue(result.ok, [(error.errorCode, error.path) for error in result.errors])
        archived = self.validator.validate_with_context(
            quantity("UNT-980006"), QUANTITY_SCHEMA, self.authoring_context
        )
        self.assertError(archived, "catalog_validation.catalog_status_not_allowed", "$.unitId")

    def test_schema_index_preserves_nested_error_paths(self) -> None:
        result = self.validator.validate_with_context(
            {"propertyRecords": [property_record(unit_id="UNT-999999")]},
            INDEX_SCHEMA,
            self.context,
        )
        self.assertError(
            result,
            "reference_integrity.reference_not_found",
            "$.propertyRecords[0].quantity.unitId",
        )


if __name__ == "__main__":
    unittest.main()
