from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.validation import EosValidator, MissingValidationDependencyError


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "valid"
VALID_KNOWLEDGE_CORE_FIXTURES = FIXTURES / "knowledge-core"
INVALID_KNOWLEDGE_CORE_FIXTURES = ROOT / "tests" / "fixtures" / "invalid" / "knowledge-core"


SOURCE_SCHEMA = "https://eos.local/schemas/source-reference.schema.json"
NORM_SCHEMA = "https://eos.local/schemas/norm-reference.schema.json"
DOCUMENT_SCHEMA = "https://eos.local/schemas/document-record.schema.json"
INDEX_SCHEMA = "https://eos.local/schemas/index.schema.json"
QUANTITY_SCHEMA = "https://eos.local/schemas/knowledge-core/quantity.schema.json"
VALUE_RANGE_SCHEMA = "https://eos.local/schemas/knowledge-core/value-range.schema.json"


def load_fixture(name: str) -> dict:
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.validator = EosValidator()
        except MissingValidationDependencyError as exc:
            raise unittest.SkipTest(f"BLOCKED missing runtime dependency: {exc}") from exc

    def assertValid(self, record: dict, schema_id: str) -> None:
        result = self.validator.validate(record, schema_id)
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def assertInvalid(self, record: dict, schema_id: str) -> None:
        result = self.validator.validate(record, schema_id)
        self.assertFalse(result.ok)

    def test_valid_source_reference_passes(self) -> None:
        self.assertValid(load_fixture("source-reference-valid.json"), SOURCE_SCHEMA)

    def test_source_reference_with_bad_id_fails(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["id"] = "src-1"
        self.assertInvalid(record, SOURCE_SCHEMA)

    def test_invalid_source_class_fails(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["sourceClass"] = "X"
        self.assertInvalid(record, SOURCE_SCHEMA)

    def test_invalid_status_fails(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["status"] = "Ready"
        self.assertInvalid(record, SOURCE_SCHEMA)

    def test_missing_required_field_fails(self) -> None:
        record = load_fixture("source-reference-valid.json")
        del record["title"]
        self.assertInvalid(record, SOURCE_SCHEMA)

    def test_unknown_field_fails_with_additional_properties_false(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["unexpected"] = "not allowed"
        self.assertInvalid(record, SOURCE_SCHEMA)

    def test_valid_norm_reference_passes(self) -> None:
        self.assertValid(load_fixture("norm-reference-valid.json"), NORM_SCHEMA)

    def test_norm_reference_without_source_link_fails(self) -> None:
        record = load_fixture("norm-reference-valid.json")
        record["sourceLinks"] = []
        self.assertInvalid(record, NORM_SCHEMA)

    def test_valid_document_record_passes(self) -> None:
        self.assertValid(load_fixture("document-record-valid.json"), DOCUMENT_SCHEMA)

    def test_swapped_document_and_schema_version_is_detected(self) -> None:
        record = load_fixture("document-record-valid.json")
        record["schemaVersion"] = "0.1"
        record["documentVersion"] = "0.2.0"
        self.assertInvalid(record, DOCUMENT_SCHEMA)

    def test_review_record_with_claims_without_source_link_fails_application_validation(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["status"] = "Review"
        result = self.validator.validate(record, SOURCE_SCHEMA, has_verifiable_claims=True)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.path == "$.sourceLinks" for error in result.errors))

    def test_draft_record_with_empty_source_links_can_pass(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["status"] = "Draft"
        record["sourceLinks"] = []
        self.assertValid(record, SOURCE_SCHEMA)

    def test_local_ref_is_supported(self) -> None:
        schema_id = "https://eos.local/test/local-ref.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "type": "object",
            "$defs": {
                "Code": {
                    "type": "string",
                    "pattern": "^OK$"
                }
            },
            "required": ["code"],
            "properties": {
                "code": { "$ref": "#/$defs/Code" }
            },
            "additionalProperties": False
        }
        self.assertValid({"code": "OK"}, schema_id)
        result = self.validator.validate({"code": "BAD"}, schema_id)
        self.assertFalse(result.ok)
        self.assertEqual(result.errors[0].path, "$.code")

    def test_invalid_datetime_fails(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["createdAt"] = "not-a-date-time"
        result = self.validator.validate(record, SOURCE_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.path == "$.createdAt" for error in result.errors))

    def test_invalid_version_format_fails(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["schemaVersion"] = "0.2"
        result = self.validator.validate(record, SOURCE_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.path == "$.schemaVersion" for error in result.errors))

    def test_bad_nested_source_link_fails_with_precise_path(self) -> None:
        record = load_fixture("norm-reference-valid.json")
        record["sourceLinks"][0]["sourceReferenceId"] = "BAD-1"
        result = self.validator.validate(record, NORM_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.path == "$.sourceLinks[0].sourceReferenceId" for error in result.errors))

    def test_unsupported_schema_keyword_fails_closed(self) -> None:
        schema_id = "https://eos.local/test/unsupported.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "type": "integer",
            "unknownEosKeyword": True
        }
        result = self.validator.validate(5, schema_id)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.category == "schema_definition" for error in result.errors))

    def test_multiple_errors_are_collected(self) -> None:
        record = load_fixture("source-reference-valid.json")
        del record["title"]
        record["id"] = "bad"
        record["status"] = "Ready"
        record["sourceClass"] = "X"
        result = self.validator.validate(record, SOURCE_SCHEMA)
        self.assertFalse(result.ok)
        paths = {error.path for error in result.errors}
        self.assertIn("$.title", paths)
        self.assertIn("$.id", paths)
        self.assertIn("$.status", paths)
        self.assertIn("$.sourceClass", paths)
        self.assertGreaterEqual(len(result.errors), 4)

    def test_all_of_works(self) -> None:
        schema_id = "https://eos.local/test/all-of.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "allOf": [
                {"type": "integer"},
                {"minimum": 2}
            ]
        }
        self.assertValid(3, schema_id)
        self.assertInvalid(1, schema_id)

    def test_one_of_works(self) -> None:
        schema_id = "https://eos.local/test/one-of.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "oneOf": [
                {"type": "string"},
                {"type": "integer"}
            ]
        }
        self.assertValid("text", schema_id)
        self.assertInvalid(True, schema_id)

    def test_if_then_else_works(self) -> None:
        schema_id = "https://eos.local/test/if-then-else.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "type": "object",
            "properties": {
                "kind": {"type": "string"},
                "code": {"type": "string"}
            },
            "if": {
                "properties": {"kind": {"const": "coded"}},
                "required": ["kind"]
            },
            "then": {"required": ["code"]},
            "else": True
        }
        self.assertValid({"kind": "plain"}, schema_id)
        self.assertInvalid({"kind": "coded"}, schema_id)

    def test_unique_items_works(self) -> None:
        schema_id = "https://eos.local/test/unique-items.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "type": "array",
            "uniqueItems": True
        }
        self.assertValid(["a", "b"], schema_id)
        self.assertInvalid(["a", "a"], schema_id)

    def test_maximum_works(self) -> None:
        schema_id = "https://eos.local/test/maximum.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "type": "integer",
            "maximum": 10
        }
        self.assertValid(10, schema_id)
        self.assertInvalid(11, schema_id)

    def test_nested_and_cross_file_ref_works(self) -> None:
        record = load_fixture("norm-reference-valid.json")
        self.assertValid(record, NORM_SCHEMA)

    def test_uri_format_checker_rejects_invalid_uri(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["uri"] = "not a uri"
        result = self.validator.validate(record, SOURCE_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.instancePath == "$.uri" for error in result.errors))

    def test_multiple_schema_errors_are_returned_together(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["id"] = "bad"
        record["status"] = "bad"
        record["createdAt"] = "bad"
        result = self.validator.validate(record, SOURCE_SCHEMA)
        self.assertFalse(result.ok)
        schema_errors = [error for error in result.errors if error.category == "schema_validation"]
        self.assertGreaterEqual(len(schema_errors), 3)

    def test_application_errors_are_separate_from_schema_validation(self) -> None:
        record = load_fixture("source-reference-valid.json")
        record["status"] = "Review"
        result = self.validator.validate(record, SOURCE_SCHEMA, has_verifiable_claims=True)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.category == "application_validation" for error in result.errors))
        self.assertFalse(any(error.category == "schema_validation" for error in result.errors))

    def test_invalid_schema_definition_is_caught(self) -> None:
        schema_id = "https://eos.local/test/invalid-schema.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "type": 5
        }
        result = self.validator.validate_schema_definition(schema_id)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.category == "schema_definition" for error in result.errors))

    def test_missing_referenced_schema_is_caught(self) -> None:
        schema_id = "https://eos.local/test/missing-ref.schema.json"
        self.validator.registry.by_id[schema_id] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": schema_id,
            "$ref": "https://eos.local/schemas/missing.schema.json"
        }
        result = self.validator.validate({}, schema_id)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.category == "schema_definition" for error in result.errors))

    def test_quantity_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(QUANTITY_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_quantity_fixtures_pass(self) -> None:
        files = sorted(VALID_KNOWLEDGE_CORE_FIXTURES.glob("quantity-*-valid.json"))
        self.assertGreaterEqual(len(files), 5)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, QUANTITY_SCHEMA)
                self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_invalid_quantity_fixtures_fail(self) -> None:
        files = sorted(INVALID_KNOWLEDGE_CORE_FIXTURES.glob("quantity-*-invalid.json"))
        self.assertGreaterEqual(len(files), 10)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, QUANTITY_SCHEMA)
                self.assertFalse(result.ok, path.name)

    def test_quantity_rejects_unknown_additional_field_with_precise_path(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "quantity-unknown-field-invalid.json")
        result = self.validator.validate(record, QUANTITY_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.path == "$.sourceLinks" for error in result.errors))

    def test_quantity_unit_id_uses_central_unt_identifier(self) -> None:
        schema = self.validator.registry.by_id[QUANTITY_SCHEMA]
        self.assertEqual(
            schema["properties"]["unitId"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/UNT",
        )
        result = self.validator.validate({"value": 1, "unitId": "UNT-000001"}, QUANTITY_SCHEMA)
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_quantity_rejects_entity_metadata_fields(self) -> None:
        metadata_fields = {
            "id": "QTY-000001",
            "schemaVersion": "0.1.0",
            "recordVersion": 1,
            "revision": 0,
            "status": "Draft",
            "sourceLinks": []
        }
        for field, value in metadata_fields.items():
            with self.subTest(field=field):
                record = {"value": 1, "unitId": "UNT-000001", field: value}
                result = self.validator.validate(record, QUANTITY_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == f"$.{field}" for error in result.errors))

    def test_quantity_multiple_errors_are_reported_with_paths(self) -> None:
        record = {
            "value": "not a number",
            "unitId": "bad",
            "unexpected": True
        }
        result = self.validator.validate(record, QUANTITY_SCHEMA)
        self.assertFalse(result.ok)
        paths = {error.path for error in result.errors}
        self.assertIn("$.value", paths)
        self.assertIn("$.unitId", paths)
        self.assertIn("$.unexpected", paths)
        self.assertGreaterEqual(len(result.errors), 3)

    def test_schema_index_resolves_quantity(self) -> None:
        record = {
            "quantities": [
                load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "quantity-integer-valid.json")
            ]
        }
        result = self.validator.validate(record, INDEX_SCHEMA)
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_quantity_rejects_non_finite_numbers(self) -> None:
        for value in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(value=value):
                result = self.validator.validate({"value": value, "unitId": "UNT-000001"}, QUANTITY_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == "$.value" for error in result.errors))

    def test_value_range_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(VALUE_RANGE_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_value_range_fixtures_pass(self) -> None:
        files = sorted(VALID_KNOWLEDGE_CORE_FIXTURES.glob("value-range-*-valid.json"))
        self.assertGreaterEqual(len(files), 8)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, VALUE_RANGE_SCHEMA)
                self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_invalid_value_range_fixtures_fail(self) -> None:
        files = sorted(INVALID_KNOWLEDGE_CORE_FIXTURES.glob("value-range-*-invalid.json"))
        self.assertGreaterEqual(len(files), 20)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, VALUE_RANGE_SCHEMA)
                self.assertFalse(result.ok, path.name)

    def test_value_range_requires_at_least_one_boundary_structurally(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "value-range-no-boundaries-invalid.json")
        result = self.validator.validate(record, VALUE_RANGE_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.category == "schema_validation" and error.path == "$" for error in result.errors))

    def test_value_range_unit_id_uses_central_unt_identifier(self) -> None:
        schema = self.validator.registry.by_id[VALUE_RANGE_SCHEMA]
        self.assertEqual(
            schema["properties"]["unitId"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/UNT",
        )
        result = self.validator.validate({"minValue": 1, "unitId": "UNT-000101"}, VALUE_RANGE_SCHEMA)
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_value_range_rejects_unknown_additional_field_with_precise_path(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "value-range-unknown-field-invalid.json")
        result = self.validator.validate(record, VALUE_RANGE_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.path == "$.unexpected" for error in result.errors))

    def test_value_range_rejects_entity_metadata_fields(self) -> None:
        metadata_fields = {
            "id": "RNG-000001",
            "schemaVersion": "0.1.0",
            "recordVersion": 1,
            "revision": 0,
            "status": "Draft"
        }
        for field, value in metadata_fields.items():
            with self.subTest(field=field):
                record = {"minValue": 1, "maxValue": 5, "unitId": "UNT-000101", field: value}
                result = self.validator.validate(record, VALUE_RANGE_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == f"$.{field}" for error in result.errors))

    def test_value_range_rejects_source_links(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "value-range-source-links-invalid.json")
        result = self.validator.validate(record, VALUE_RANGE_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.path == "$.sourceLinks" for error in result.errors))

    def test_value_range_reversed_bounds_are_application_validation(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "value-range-reversed-bounds-invalid.json")
        result = self.validator.validate(record, VALUE_RANGE_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(
            any(
                error.category == "application_validation"
                and error.errorCode == "application_validation.value_range_reversed_bounds"
                and error.path == "$.minValue"
                for error in result.errors
            )
        )

    def test_value_range_inclusivity_without_boundary_is_application_validation(self) -> None:
        cases = [
            (
                "value-range-lower-inclusive-without-min-invalid.json",
                "application_validation.value_range_lower_inclusive_without_min",
                "$.lowerInclusive",
            ),
            (
                "value-range-upper-inclusive-without-max-invalid.json",
                "application_validation.value_range_upper_inclusive_without_max",
                "$.upperInclusive",
            ),
        ]
        for filename, error_code, path in cases:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, VALUE_RANGE_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(
                    any(
                        error.category == "application_validation"
                        and error.errorCode == error_code
                        and error.path == path
                        for error in result.errors
                    )
                )

    def test_value_range_equal_boundaries_are_valid(self) -> None:
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "value-range-equal-boundaries-valid.json")
        self.assertValid(record, VALUE_RANGE_SCHEMA)

    def test_value_range_single_sided_ranges_are_valid(self) -> None:
        for filename in [
            "value-range-lower-bounded-valid.json",
            "value-range-upper-bounded-valid.json",
        ]:
            with self.subTest(filename=filename):
                record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / filename)
                self.assertValid(record, VALUE_RANGE_SCHEMA)

    def test_value_range_schema_and_application_errors_are_distinguishable(self) -> None:
        record = {
            "minValue": 5,
            "maxValue": 1,
            "unitId": "bad"
        }
        result = self.validator.validate(record, VALUE_RANGE_SCHEMA)
        self.assertFalse(result.ok)
        categories = {error.category for error in result.errors}
        self.assertIn("schema_validation", categories)
        self.assertIn("application_validation", categories)

    def test_schema_index_resolves_value_range(self) -> None:
        record = {
            "valueRanges": [
                load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "value-range-closed-valid.json")
            ]
        }
        result = self.validator.validate(record, INDEX_SCHEMA)
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])


if __name__ == "__main__":
    unittest.main()
