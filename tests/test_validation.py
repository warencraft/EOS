from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.validation import EosValidator, MissingValidationDependencyError


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "valid"
VALID_KNOWLEDGE_CORE_FIXTURES = FIXTURES / "knowledge-core"
INVALID_KNOWLEDGE_CORE_FIXTURES = ROOT / "tests" / "fixtures" / "invalid" / "knowledge-core"
VALID_CATALOG_FIXTURES = FIXTURES / "catalogs"
INVALID_CATALOG_FIXTURES = ROOT / "tests" / "fixtures" / "invalid" / "catalogs"
VALID_ENTITY_FIXTURES = FIXTURES / "entities"
INVALID_ENTITY_FIXTURES = ROOT / "tests" / "fixtures" / "invalid" / "entities"


SOURCE_SCHEMA = "https://eos.local/schemas/source-reference.schema.json"
NORM_SCHEMA = "https://eos.local/schemas/norm-reference.schema.json"
DOCUMENT_SCHEMA = "https://eos.local/schemas/document-record.schema.json"
INDEX_SCHEMA = "https://eos.local/schemas/index.schema.json"
QUANTITY_SCHEMA = "https://eos.local/schemas/knowledge-core/quantity.schema.json"
VALUE_RANGE_SCHEMA = "https://eos.local/schemas/knowledge-core/value-range.schema.json"
MEASUREMENT_QUALITY_SCHEMA = "https://eos.local/schemas/knowledge-core/measurement-quality.schema.json"
CONDITION_SCHEMA = "https://eos.local/schemas/knowledge-core/condition.schema.json"
CLASSIFICATION_SCHEMA = "https://eos.local/schemas/knowledge-core/classification.schema.json"
PROPERTY_RECORD_SCHEMA = "https://eos.local/schemas/knowledge-core/property-record.schema.json"
OBSERVATION_SCHEMA = "https://eos.local/schemas/knowledge-core/observation.schema.json"
UNIT_CATALOG_ENTRY_SCHEMA = "https://eos.local/schemas/catalogs/unit-catalog-entry.schema.json"
CONDITION_TYPE_CATALOG_ENTRY_SCHEMA = "https://eos.local/schemas/catalogs/condition-type-catalog-entry.schema.json"
PROPERTY_CATALOG_ENTRY_SCHEMA = "https://eos.local/schemas/catalogs/property-catalog-entry.schema.json"
CLASSIFICATION_CATALOG_ENTRY_SCHEMA = "https://eos.local/schemas/catalogs/classification-catalog-entry.schema.json"
MATERIAL_SCHEMA = "https://eos.local/schemas/entities/material.schema.json"


def load_fixture(name: str) -> dict:
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def setUpModule() -> None:
    try:
        EosValidator()
    except MissingValidationDependencyError as exc:
        raise RuntimeError(f"Validation test suite blocked: {exc}") from exc


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = EosValidator()

    def test_required_validation_dependencies_fail_closed(self) -> None:
        simulation = """
import builtins
import sys
import unittest

blocked = sys.argv[1]
real_import = builtins.__import__

def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == blocked or name.startswith(blocked + "."):
        error = ModuleNotFoundError(f"No module named '{blocked}'")
        error.name = blocked
        raise error
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = guarded_import
suite = unittest.defaultTestLoader.discover("tests")
result = unittest.TextTestRunner(verbosity=0).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
"""
        for dependency in ["jsonschema", "referencing"]:
            with self.subTest(dependency=dependency):
                completed = subprocess.run(
                    [sys.executable, "-c", simulation, dependency],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                output = completed.stdout + completed.stderr
                self.assertNotEqual(completed.returncode, 0, output)
                self.assertIn(
                    f"Missing required validation dependency '{dependency}'",
                    output,
                )
                self.assertIn("python -m venv .venv", output)
                self.assertIn("pip install -e .", output)

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

    def test_measurement_quality_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(MEASUREMENT_QUALITY_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_measurement_quality_fixtures_pass(self) -> None:
        files = sorted(VALID_KNOWLEDGE_CORE_FIXTURES.glob("measurement-quality-*-valid.json"))
        self.assertGreaterEqual(len(files), 10)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, MEASUREMENT_QUALITY_SCHEMA)
                self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_invalid_measurement_quality_fixtures_fail(self) -> None:
        files = sorted(INVALID_KNOWLEDGE_CORE_FIXTURES.glob("measurement-quality-*-invalid.json"))
        self.assertGreaterEqual(len(files), 29)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, MEASUREMENT_QUALITY_SCHEMA)
                self.assertFalse(result.ok, path.name)

    def test_measurement_quality_quantity_ref_resolves(self) -> None:
        schema = self.validator.registry.by_id[MEASUREMENT_QUALITY_SCHEMA]
        self.assertEqual(
            schema["properties"]["uncertainty"]["$ref"],
            "https://eos.local/schemas/knowledge-core/quantity.schema.json",
        )
        self.assertEqual(
            schema["properties"]["resolution"]["$ref"],
            "https://eos.local/schemas/knowledge-core/quantity.schema.json",
        )

    def test_measurement_quality_notes_only_and_empty_object_fail(self) -> None:
        for filename in [
            "measurement-quality-empty-object-invalid.json",
            "measurement-quality-notes-only-invalid.json",
        ]:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, MEASUREMENT_QUALITY_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.category == "schema_validation" for error in result.errors))

    def test_measurement_quality_confidence_level_boundaries(self) -> None:
        for confidence_level in [0, 1]:
            with self.subTest(confidence_level=confidence_level):
                result = self.validator.validate({"confidenceLevel": confidence_level}, MEASUREMENT_QUALITY_SCHEMA)
                self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

        for confidence_level in [-0.1, 1.1]:
            with self.subTest(confidence_level=confidence_level):
                result = self.validator.validate({"confidenceLevel": confidence_level}, MEASUREMENT_QUALITY_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == "$.confidenceLevel" for error in result.errors))

    def test_measurement_quality_negative_uncertainty_is_application_validation(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "measurement-quality-negative-uncertainty-invalid.json")
        result = self.validator.validate(record, MEASUREMENT_QUALITY_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(
            any(
                error.category == "application_validation"
                and error.errorCode == "application_validation.measurement_quality_negative_uncertainty"
                and error.path == "$.uncertainty.value"
                for error in result.errors
            )
        )

    def test_measurement_quality_zero_uncertainty_passes(self) -> None:
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "measurement-quality-zero-uncertainty-valid.json")
        self.assertValid(record, MEASUREMENT_QUALITY_SCHEMA)

    def test_measurement_quality_nonpositive_resolution_is_application_validation(self) -> None:
        cases = [
            "measurement-quality-zero-resolution-invalid.json",
            "measurement-quality-negative-resolution-invalid.json",
        ]
        for filename in cases:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, MEASUREMENT_QUALITY_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(
                    any(
                        error.category == "application_validation"
                        and error.errorCode == "application_validation.measurement_quality_nonpositive_resolution"
                        and error.path == "$.resolution.value"
                        for error in result.errors
                    )
                )

    def test_measurement_quality_tolerance_and_deferred_fields_fail(self) -> None:
        cases = [
            ("measurement-quality-tolerance-field-invalid.json", "$.tolerance"),
            ("measurement-quality-upper-tolerance-field-invalid.json", "$.upperTolerance"),
            ("measurement-quality-lower-tolerance-field-invalid.json", "$.lowerTolerance"),
            ("measurement-quality-accuracy-field-invalid.json", "$.accuracy"),
            ("measurement-quality-repeatability-field-invalid.json", "$.repeatability"),
            ("measurement-quality-reproducibility-field-invalid.json", "$.reproducibility"),
        ]
        for filename, path in cases:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, MEASUREMENT_QUALITY_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == path for error in result.errors))

    def test_measurement_quality_metadata_source_and_status_fields_fail(self) -> None:
        cases = [
            ("measurement-quality-entity-metadata-invalid.json", "$.id"),
            ("measurement-quality-lifecycle-field-invalid.json", "$.status"),
            ("measurement-quality-source-links-invalid.json", "$.sourceLinks"),
            ("measurement-quality-verification-status-invalid.json", "$.verificationStatus"),
        ]
        for filename, path in cases:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, MEASUREMENT_QUALITY_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == path for error in result.errors))

    def test_measurement_quality_nested_error_path_identifies_quantity_value(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "measurement-quality-invalid-nested-quantity-invalid.json")
        result = self.validator.validate(record, MEASUREMENT_QUALITY_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.path == "$.uncertainty.value" for error in result.errors))

    def test_measurement_quality_schema_and_application_errors_are_distinguishable(self) -> None:
        record = {
            "uncertainty": {
                "value": -1,
                "unitId": "bad"
            }
        }
        result = self.validator.validate(record, MEASUREMENT_QUALITY_SCHEMA)
        self.assertFalse(result.ok)
        categories = {error.category for error in result.errors}
        self.assertIn("schema_validation", categories)
        self.assertIn("application_validation", categories)

    def test_schema_index_resolves_measurement_quality(self) -> None:
        record = {
            "measurementQualities": [
                load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "measurement-quality-confidence-only-valid.json")
            ]
        }
        result = self.validator.validate(record, INDEX_SCHEMA)
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_condition_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(CONDITION_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_condition_fixtures_pass(self) -> None:
        files = sorted(VALID_KNOWLEDGE_CORE_FIXTURES.glob("condition-*-valid.json"))
        self.assertGreaterEqual(len(files), 7)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, CONDITION_SCHEMA)
                self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_invalid_condition_fixtures_fail(self) -> None:
        files = sorted(INVALID_KNOWLEDGE_CORE_FIXTURES.glob("condition-*-invalid.json"))
        self.assertGreaterEqual(len(files), 31)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, CONDITION_SCHEMA)
                self.assertFalse(result.ok, path.name)

    def test_condition_type_id_uses_central_cnd_identifier(self) -> None:
        identifiers = self.validator.registry.by_id["https://eos.local/schemas/common/identifiers.schema.json"]
        schema = self.validator.registry.by_id[CONDITION_SCHEMA]
        self.assertEqual(identifiers["$defs"]["CND"]["pattern"], "^CND-[0-9]{6}$")
        self.assertEqual(
            schema["properties"]["conditionTypeId"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/CND",
        )
        result = self.validator.validate(
            {
                "conditionTypeId": "CND-000010",
                "evaluationMode": "mandatory",
                "textValue": "fictional context",
            },
            CONDITION_SCHEMA,
        )
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_condition_evaluation_modes_are_accepted(self) -> None:
        for index, mode in enumerate(["mandatory", "limiting", "descriptive", "recommended", "contextual"], start=1):
            with self.subTest(mode=mode):
                record = {
                    "conditionTypeId": f"CND-00001{index}",
                    "evaluationMode": mode,
                    "textValue": "fictional context",
                }
                self.assertValid(record, CONDITION_SCHEMA)

    def test_condition_invalid_evaluation_mode_fails_with_path(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "condition-invalid-evaluation-mode-invalid.json")
        result = self.validator.validate(record, CONDITION_SCHEMA)
        self.assertFalse(result.ok)
        self.assertTrue(any(error.category == "schema_validation" and error.path == "$.evaluationMode" for error in result.errors))

    def test_condition_requires_exactly_one_value_form(self) -> None:
        cases = [
            "condition-no-value-form-invalid.json",
            "condition-notes-only-invalid.json",
            "condition-quantity-and-value-range-invalid.json",
            "condition-quantity-and-text-invalid.json",
            "condition-boolean-and-reference-invalid.json",
            "condition-all-value-forms-invalid.json",
        ]
        for filename in cases:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, CONDITION_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.category == "schema_validation" and error.errorCode == "schema_validation.oneOf" for error in result.errors))

    def test_condition_quantity_and_value_range_refs_resolve(self) -> None:
        schema = self.validator.registry.by_id[CONDITION_SCHEMA]
        self.assertEqual(
            schema["properties"]["quantity"]["$ref"],
            "https://eos.local/schemas/knowledge-core/quantity.schema.json",
        )
        self.assertEqual(
            schema["properties"]["valueRange"]["$ref"],
            "https://eos.local/schemas/knowledge-core/value-range.schema.json",
        )
        self.assertValid(load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "condition-quantity-valid.json"), CONDITION_SCHEMA)
        self.assertValid(load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "condition-value-range-valid.json"), CONDITION_SCHEMA)

    def test_condition_nested_error_paths_identify_fields(self) -> None:
        cases = [
            ("condition-invalid-nested-quantity-invalid.json", "$.quantity.value"),
            ("condition-invalid-nested-value-range-invalid.json", "$.valueRange.minValue"),
        ]
        for filename, expected_path in cases:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, CONDITION_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == expected_path for error in result.errors))

    def test_condition_empty_text_and_reference_fail_with_paths(self) -> None:
        cases = [
            ("condition-empty-text-value-invalid.json", "$.textValue"),
            ("condition-empty-reference-id-invalid.json", "$.referenceId"),
        ]
        for filename, expected_path in cases:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, CONDITION_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == expected_path for error in result.errors))

    def test_condition_metadata_source_and_status_fields_fail(self) -> None:
        cases = [
            ("condition-entity-metadata-invalid.json", "$.id"),
            ("condition-lifecycle-field-invalid.json", "$.status"),
            ("condition-source-links-invalid.json", "$.sourceLinks"),
            ("condition-verification-status-invalid.json", "$.verificationStatus"),
            ("condition-property-id-invalid.json", "$.propertyId"),
        ]
        for filename, expected_path in cases:
            with self.subTest(filename=filename):
                record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / filename)
                result = self.validator.validate(record, CONDITION_SCHEMA)
                self.assertFalse(result.ok)
                self.assertTrue(any(error.path == expected_path for error in result.errors))

    def test_condition_reference_id_uses_existing_supported_identifiers(self) -> None:
        schema = self.validator.registry.by_id[CONDITION_SCHEMA]
        reference_targets = {
            ref["$ref"].rsplit("/", 1)[-1]
            for ref in schema["properties"]["referenceId"]["anyOf"]
        }
        self.assertIn("SRC", reference_targets)
        self.assertIn("CND", reference_targets)
        self.assertNotIn("REL", reference_targets)

        valid_record = {
            "conditionTypeId": "CND-000020",
            "evaluationMode": "contextual",
            "referenceId": "SRC-000001",
        }
        invalid_record = {
            "conditionTypeId": "CND-000020",
            "evaluationMode": "contextual",
            "referenceId": "REL-000001",
        }
        self.assertValid(valid_record, CONDITION_SCHEMA)
        self.assertInvalid(invalid_record, CONDITION_SCHEMA)

    def test_condition_schema_index_resolves_condition(self) -> None:
        record = {
            "conditions": [
                load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "condition-text-valid.json")
            ]
        }
        result = self.validator.validate(record, INDEX_SCHEMA)
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_condition_validation_is_schema_only_for_contract_rules(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "condition-notes-only-invalid.json")
        result = self.validator.validate(record, CONDITION_SCHEMA)
        self.assertFalse(result.ok)
        categories = {error.category for error in result.errors}
        self.assertIn("schema_validation", categories)
        self.assertNotIn("application_validation", categories)


    def test_classification_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(CLASSIFICATION_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_classification_fixtures_pass(self) -> None:
        files = sorted(VALID_KNOWLEDGE_CORE_FIXTURES.glob("classification-*-valid.json"))
        self.assertGreaterEqual(len(files), 4)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, CLASSIFICATION_SCHEMA)
                self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_invalid_classification_fixtures_fail_for_expected_reason(self) -> None:
        cases = {
            "empty-object": ("required", "$.classificationId"),
            "missing-classification-id": ("required", "$.classificationId"),
            "invalid-cls-prefix": ("pattern", "$.classificationId"),
            "lowercase-cls-prefix": ("pattern", "$.classificationId"),
            "incomplete-cls-padding": ("pattern", "$.classificationId"),
            "null-classification-id": ("type", "$.classificationId"),
            "numeric-classification-id": ("type", "$.classificationId"),
            "unknown-root-field": ("additionalProperties", "$.unexpected"),
            "id-field": ("additionalProperties", "$.id"),
            "status-field": ("additionalProperties", "$.status"),
            "lifecycle-field": ("additionalProperties", "$.lifecycle"),
            "verification-status-field": ("additionalProperties", "$.verificationStatus"),
            "evaluation-mode-field": ("additionalProperties", "$.evaluationMode"),
            "text-value-field": ("additionalProperties", "$.textValue"),
            "label-field": ("additionalProperties", "$.label"),
            "code-field": ("additionalProperties", "$.code"),
            "enum-field": ("additionalProperties", "$.enum"),
            "value-field": ("additionalProperties", "$.value"),
            "notes-field": ("additionalProperties", "$.notes"),
            "malformed-source-links": ("type", "$.sourceLinks[0]"),
            "invalid-nested-source-link": ("required", "$.sourceLinks[0].verificationStatus"),
            "null-source-links": ("type", "$.sourceLinks"),
            "wrong-type-source-links": ("type", "$.sourceLinks"),
            "array-instead-of-object": ("type", "$"),
            "invalid-source-reference-id": ("pattern", "$.sourceLinks[0].sourceReferenceId"),
            "unknown-source-link-field": ("additionalProperties", "$.sourceLinks[0].unexpected"),
        }
        expected_names = {f"classification-{name}-invalid.json" for name in cases}
        files = {path.name for path in INVALID_KNOWLEDGE_CORE_FIXTURES.glob("classification-*-invalid.json")}
        self.assertEqual(files, expected_names)
        for name, (keyword, expected_path) in cases.items():
            with self.subTest(case=name):
                path = INVALID_KNOWLEDGE_CORE_FIXTURES / f"classification-{name}-invalid.json"
                result = self.validator.validate_json_file(path, CLASSIFICATION_SCHEMA)
                self.assertFalse(result.ok)
                self.assertIn(
                    ("schema_validation", f"schema_validation.{keyword}", expected_path),
                    {(e.category, e.errorCode, e.path) for e in result.errors},
                )

    def test_classification_uses_central_cls_identifier(self) -> None:
        schema = self.validator.registry.by_id[CLASSIFICATION_SCHEMA]
        self.assertEqual(
            schema["properties"]["classificationId"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/CLS",
        )
        for identifier in ["CLS-000000", "CLS-999999"]:
            with self.subTest(identifier=identifier):
                self.assertValid({"classificationId": identifier}, CLASSIFICATION_SCHEMA)
        for identifier in ["CLS-0000001", "CLS-12345", "CLS-abcdef", ["CLS-000001"]]:
            with self.subTest(identifier=identifier):
                self.assertInvalid({"classificationId": identifier}, CLASSIFICATION_SCHEMA)

    def test_classification_reuses_common_source_link(self) -> None:
        schema = self.validator.registry.by_id[CLASSIFICATION_SCHEMA]
        self.assertEqual(
            schema["properties"]["sourceLinks"]["items"],
            {"$ref": "https://eos.local/schemas/common/source-link.schema.json"},
        )
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "classification-one-source-link-valid.json")
        self.assertValid(record, CLASSIFICATION_SCHEMA)
        record["sourceLinks"][0]["verificationStatus"] = "not-a-status"
        result = self.validator.validate(record, CLASSIFICATION_SCHEMA)
        self.assertIn(
            ("schema_validation.enum", "$.sourceLinks[0].verificationStatus"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_classification_source_links_are_structurally_optional(self) -> None:
        for record in [
            {"classificationId": "CLS-000001"},
            {"classificationId": "CLS-000001", "sourceLinks": []},
        ]:
            with self.subTest(record=record):
                self.assertValid(record, CLASSIFICATION_SCHEMA)

    def test_classification_source_link_multiplicity_matches_common_metadata(self) -> None:
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "classification-multiple-source-links-valid.json")
        self.assertValid(record, CLASSIFICATION_SCHEMA)
        record["sourceLinks"].append(record["sourceLinks"][0].copy())
        self.assertValid(record, CLASSIFICATION_SCHEMA)

    def test_classification_rejects_all_excluded_root_fields(self) -> None:
        fields = [
            "id", "classificationTypeId", "classificationEntryId", "catalogId",
            "systemId", "namespace", "code", "value", "textValue", "label",
            "enum", "fallbackText", "notes", "evaluationMode", "verificationStatus",
            "status", "revision", "lifecycle", "parentClassificationId",
            "hierarchyPath", "level", "validFrom", "validUntil", "schemaVersion",
            "recordVersion", "createdAt", "createdBy", "updatedAt", "updatedBy",
        ]
        for field in fields:
            with self.subTest(field=field):
                result = self.validator.validate(
                    {"classificationId": "CLS-000001", field: "fictional"}, CLASSIFICATION_SCHEMA,
                )
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field}"),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_classification_index_resolves_multiple_classifications_and_nested_errors(self) -> None:
        record = {"classifications": [
            {"classificationId": "CLS-000001"},
            load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "classification-one-source-link-valid.json"),
        ]}
        self.assertValid(record, INDEX_SCHEMA)
        record["classifications"][1]["sourceLinks"][0]["sourceClass"] = "invalid"
        result = self.validator.validate(record, INDEX_SCHEMA)
        self.assertIn(
            ("schema_validation.enum", "$.classifications[1].sourceLinks[0].sourceClass"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_classification_collects_multiple_schema_errors(self) -> None:
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "classification-one-source-link-valid.json")
        record["classificationId"] = "bad"
        record["sourceLinks"][0]["sourceClass"] = "bad"
        record["notes"] = "not permitted"
        result = self.validator.validate(record, CLASSIFICATION_SCHEMA)
        self.assertEqual(len(result.errors), 3)
        self.assertEqual({e.category for e in result.errors}, {"schema_validation"})
        self.assertEqual({e.path for e in result.errors}, {
            "$.classificationId", "$.sourceLinks[0].sourceClass", "$.notes",
        })

    def test_classification_does_not_infer_catalog_origin_or_existence(self) -> None:
        result = self.validator.validate(
            {"classificationId": "CLS-999999"}, CLASSIFICATION_SCHEMA, has_verifiable_claims=True,
        )
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_classification_source_reference_format_is_schema_validation(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "classification-invalid-source-reference-id-invalid.json")
        result = self.validator.validate(record, CLASSIFICATION_SCHEMA)
        self.assertEqual({e.category for e in result.errors}, {"schema_validation"})
        self.assertEqual(
            {e.errorCode for e in result.errors},
            {"schema_validation.pattern"},
        )
        self.assertTrue(all(e.path == "$.sourceLinks[0].sourceReferenceId" for e in result.errors))

    def test_well_formed_source_reference_defers_existence_validation(self) -> None:
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "classification-one-source-link-valid.json")
        record["sourceLinks"][0]["sourceReferenceId"] = "SRC-999999"
        result = self.validator.validate(record, CLASSIFICATION_SCHEMA)
        self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])
        self.assertNotIn("reference_integrity", {e.category for e in result.errors})


    def test_property_record_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(PROPERTY_RECORD_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_property_record_fixtures_pass(self) -> None:
        files = sorted(VALID_KNOWLEDGE_CORE_FIXTURES.glob("property-record-*-valid.json"))
        self.assertEqual(len(files), 10)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, PROPERTY_RECORD_SCHEMA)
                self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_invalid_property_record_fixtures_fail(self) -> None:
        files = sorted(INVALID_KNOWLEDGE_CORE_FIXTURES.glob("property-record-*-invalid.json"))
        self.assertEqual(len(files), 40)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, PROPERTY_RECORD_SCHEMA)
                self.assertFalse(result.ok, path.name)

    def test_property_record_uses_central_prp_identifier(self) -> None:
        schema = self.validator.registry.by_id[PROPERTY_RECORD_SCHEMA]
        self.assertEqual(
            schema["properties"]["propertyId"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/PRP",
        )
        valid = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "property-record-quantity-valid.json")
        valid["propertyId"] = "PRP-999999"
        self.assertValid(valid, PROPERTY_RECORD_SCHEMA)

    def test_property_record_discriminator_requires_exactly_one_branch(self) -> None:
        names = [
            "property-record-quantity-missing-branch-invalid.json",
            "property-record-value-range-missing-branch-invalid.json",
            "property-record-quantity-type-with-range-invalid.json",
            "property-record-range-type-with-quantity-invalid.json",
            "property-record-both-branches-invalid.json",
            "property-record-neither-branch-invalid.json",
        ]
        for name in names:
            with self.subTest(name=name):
                self.assertInvalid(load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / name), PROPERTY_RECORD_SCHEMA)

    def test_property_record_reuses_required_contracts(self) -> None:
        schema = self.validator.registry.by_id[PROPERTY_RECORD_SCHEMA]
        expected_refs = {
            "quantity": QUANTITY_SCHEMA,
            "valueRange": VALUE_RANGE_SCHEMA,
            "measurementQuality": MEASUREMENT_QUALITY_SCHEMA,
            "verificationStatus": (
                "https://eos.local/schemas/common/lifecycle-status.schema.json#/$defs/VerificationStatus"
            ),
        }
        for field, expected_ref in expected_refs.items():
            with self.subTest(field=field):
                self.assertEqual(schema["properties"][field]["$ref"], expected_ref)
        self.assertEqual(schema["properties"]["conditions"]["items"]["$ref"], CONDITION_SCHEMA)
        self.assertEqual(
            schema["properties"]["sourceLinks"]["items"]["$ref"],
            "https://eos.local/schemas/common/source-link.schema.json",
        )

    def test_property_record_source_links_are_required_but_may_be_empty(self) -> None:
        empty = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "property-record-empty-source-links-valid.json")
        self.assertValid(empty, PROPERTY_RECORD_SCHEMA)
        missing = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "property-record-missing-source-links-invalid.json")
        result = self.validator.validate(missing, PROPERTY_RECORD_SCHEMA)
        self.assertIn(
            ("schema_validation.required", "$.sourceLinks"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_property_record_rejects_deferred_and_lifecycle_fields(self) -> None:
        cases = {
            "textValue": "fictional",
            "booleanValue": True,
            "referenceId": "SRC-000001",
            "classification": {"classificationId": "CLS-000001"},
            "notes": "fictional",
            "id": "PRC-000001",
            "revision": 0,
            "status": "Draft",
            "lifecycle": "Draft",
            "observationId": "OBS-000001",
            "decisionId": "DEC-000001",
        }
        base = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "property-record-quantity-valid.json")
        for field, value in cases.items():
            with self.subTest(field=field):
                result = self.validator.validate({**base, field: value}, PROPERTY_RECORD_SCHEMA)
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field}"),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_property_record_nested_reversed_range_is_application_validation(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "property-record-reversed-value-range-invalid.json")
        result = self.validator.validate(record, PROPERTY_RECORD_SCHEMA)
        self.assertIn(
            (
                "application_validation",
                "application_validation.value_range_reversed_bounds",
                "$.valueRange.minValue",
            ),
            {(e.category, e.errorCode, e.path) for e in result.errors},
        )

    def test_property_record_nested_measurement_quality_application_rules(self) -> None:
        cases = [
            (
                "property-record-negative-uncertainty-invalid.json",
                "application_validation.measurement_quality_negative_uncertainty",
                "$.measurementQuality.uncertainty.value",
            ),
            (
                "property-record-zero-resolution-invalid.json",
                "application_validation.measurement_quality_nonpositive_resolution",
                "$.measurementQuality.resolution.value",
            ),
        ]
        for name, code, path in cases:
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / name), PROPERTY_RECORD_SCHEMA,
                )
                self.assertIn(
                    ("application_validation", code, path),
                    {(e.category, e.errorCode, e.path) for e in result.errors},
                )

    def test_nested_condition_contract_rules_are_composed(self) -> None:
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "property-record-one-condition-valid.json")
        record["conditions"][0] = {
            "conditionTypeId": "CND-000001",
            "evaluationMode": "limiting",
            "valueRange": {"minValue": 2, "maxValue": 1, "unitId": "UNT-000001"},
        }
        result = self.validator.validate(record, PROPERTY_RECORD_SCHEMA)
        self.assertIn(
            (
                "application_validation.value_range_reversed_bounds",
                "$.conditions[0].valueRange.minValue",
            ),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_property_record_schema_and_application_errors_remain_distinct(self) -> None:
        record = load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / "property-record-reversed-value-range-invalid.json")
        record["propertyId"] = "bad"
        result = self.validator.validate(record, PROPERTY_RECORD_SCHEMA)
        self.assertEqual(
            {"schema_validation", "application_validation"},
            {e.category for e in result.errors},
        )

    def test_property_record_schema_index_resolves(self) -> None:
        record = {
            "propertyRecords": [
                load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "property-record-quantity-valid.json")
            ]
        }
        self.assertValid(record, INDEX_SCHEMA)
        record["propertyRecords"][0] = load_json(
            INVALID_KNOWLEDGE_CORE_FIXTURES / "property-record-reversed-value-range-invalid.json"
        )
        result = self.validator.validate(record, INDEX_SCHEMA)
        self.assertIn(
            (
                "application_validation.value_range_reversed_bounds",
                "$.propertyRecords[0].valueRange.minValue",
            ),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_observation_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(OBSERVATION_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_observation_fixtures_pass(self) -> None:
        files = sorted(VALID_KNOWLEDGE_CORE_FIXTURES.glob("observation-*-valid.json"))
        self.assertEqual(len(files), 10)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, OBSERVATION_SCHEMA)
                self.assertTrue(result.ok, [f"{e.path}: {e.message}" for e in result.errors])

    def test_invalid_observation_fixtures_fail(self) -> None:
        files = sorted(INVALID_KNOWLEDGE_CORE_FIXTURES.glob("observation-*-invalid.json"))
        self.assertEqual(len(files), 45)
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate_json_file(path, OBSERVATION_SCHEMA)
                self.assertFalse(result.ok, path.name)

    def test_observation_uses_central_obs_and_prp_identifiers(self) -> None:
        schema = self.validator.registry.by_id[OBSERVATION_SCHEMA]
        self.assertEqual(
            schema["properties"]["id"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/OBS",
        )
        self.assertEqual(
            schema["properties"]["propertyId"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/PRP",
        )
        identifiers = self.validator.registry.by_id[
            "https://eos.local/schemas/common/identifiers.schema.json"
        ]
        self.assertEqual(identifiers["$defs"]["OBS"]["pattern"], "^OBS-[0-9]{6}$")

    def test_observation_subject_identifier_families(self) -> None:
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "observation-global-quantity-valid.json")
        subject_ids = [
            "MAT-0001", "POL-0001", "TEC-0001", "MAC-0001", "TOOL-0001",
            "SUP-0001", "JOB-2026-0001", "JOB-2026-0001-OP-001",
        ]
        for subject_id in subject_ids:
            with self.subTest(subject_id=subject_id):
                self.assertValid({**record, "subjectId": subject_id}, OBSERVATION_SCHEMA)
        for subject_id in ["SRC-000001", "MAT-1", "PROJECT-0001"]:
            with self.subTest(rejected_subject_id=subject_id):
                self.assertInvalid({**record, "subjectId": subject_id}, OBSERVATION_SCHEMA)

    def test_observation_global_and_job_scope_rules(self) -> None:
        global_record = load_json(
            VALID_KNOWLEDGE_CORE_FIXTURES / "observation-global-quantity-valid.json"
        )
        self.assertValid(global_record, OBSERVATION_SCHEMA)
        self.assertInvalid(
            {**global_record, "scopeReferenceId": "JOB-2026-0001"}, OBSERVATION_SCHEMA,
        )
        job_record = {**global_record, "observationScope": "JOB"}
        self.assertInvalid(job_record, OBSERVATION_SCHEMA)
        self.assertValid(
            {**job_record, "scopeReferenceId": "JOB-2026-0001"}, OBSERVATION_SCHEMA,
        )
        self.assertInvalid(
            {**job_record, "scopeReferenceId": "MAT-0001"}, OBSERVATION_SCHEMA,
        )
        for scope in ["PROJECT", "EXPERIMENT"]:
            with self.subTest(scope=scope):
                self.assertInvalid({**global_record, "observationScope": scope}, OBSERVATION_SCHEMA)

    def test_observation_result_discriminator_and_exactly_one_branch(self) -> None:
        names = [
            "observation-quantity-type-without-quantity-invalid.json",
            "observation-value-range-type-without-range-invalid.json",
            "observation-both-result-branches-invalid.json",
            "observation-neither-result-branch-invalid.json",
            "observation-invalid-value-type-invalid.json",
        ]
        for name in names:
            with self.subTest(name=name):
                self.assertInvalid(load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / name), OBSERVATION_SCHEMA)

    def test_observation_rejects_claim_generic_and_deferred_fields(self) -> None:
        base = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "observation-global-quantity-valid.json")
        cases = {
            "propertyRecord": {"propertyId": "PRP-000001"},
            "payload": {"value": "fictional"},
            "textValue": "fictional",
            "observationId": "OBS-000002",
            "subjectType": "Material",
            "recordedAt": "2026-09-08T10:00:00Z",
            "verificationStatus": "Draft",
            "supersedesObservationId": "OBS-000002",
            "observationType": "measurement",
            "observedBy": "example-user",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                result = self.validator.validate({**base, field: value}, OBSERVATION_SCHEMA)
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field}"),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_observation_reuses_numeric_quality_condition_and_source_contracts(self) -> None:
        schema = self.validator.registry.by_id[OBSERVATION_SCHEMA]
        expected_refs = {
            "quantity": QUANTITY_SCHEMA,
            "valueRange": VALUE_RANGE_SCHEMA,
            "measurementQuality": MEASUREMENT_QUALITY_SCHEMA,
        }
        for field, expected_ref in expected_refs.items():
            with self.subTest(field=field):
                self.assertEqual(schema["properties"][field]["$ref"], expected_ref)
        self.assertEqual(schema["properties"]["conditions"]["items"]["$ref"], CONDITION_SCHEMA)
        self.assertEqual(
            schema["properties"]["sourceLinks"]["$ref"],
            "https://eos.local/schemas/common/metadata.schema.json#/properties/sourceLinks",
        )

    def test_observation_nested_reversed_range_is_application_validation(self) -> None:
        record = load_json(
            INVALID_KNOWLEDGE_CORE_FIXTURES / "observation-reversed-nested-value-range-invalid.json"
        )
        result = self.validator.validate(record, OBSERVATION_SCHEMA)
        self.assertIn(
            (
                "application_validation.value_range_reversed_bounds",
                "$.valueRange.minValue",
            ),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_observation_nested_measurement_quality_rules(self) -> None:
        cases = [
            (
                "observation-negative-uncertainty-invalid.json",
                "application_validation.measurement_quality_negative_uncertainty",
                "$.measurementQuality.uncertainty.value",
            ),
            (
                "observation-zero-resolution-invalid.json",
                "application_validation.measurement_quality_nonpositive_resolution",
                "$.measurementQuality.resolution.value",
            ),
        ]
        for name, code, path in cases:
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / name), OBSERVATION_SCHEMA,
                )
                self.assertIn((code, path), {(e.errorCode, e.path) for e in result.errors})

    def test_observation_nested_condition_rules_are_composed(self) -> None:
        record = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "observation-one-condition-valid.json")
        record["conditions"][0] = {
            "conditionTypeId": "CND-000001",
            "evaluationMode": "limiting",
            "valueRange": {"minValue": 2, "maxValue": 1, "unitId": "UNT-000001"},
        }
        result = self.validator.validate(record, OBSERVATION_SCHEMA)
        self.assertIn(
            (
                "application_validation.value_range_reversed_bounds",
                "$.conditions[0].valueRange.minValue",
            ),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_observation_source_links_structure_and_lifecycle_rule(self) -> None:
        draft = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "observation-empty-source-links-valid.json")
        self.assertValid(draft, OBSERVATION_SCHEMA)
        missing = dict(draft)
        del missing["sourceLinks"]
        result = self.validator.validate(missing, OBSERVATION_SCHEMA)
        self.assertIn(
            ("schema_validation.required", "$.sourceLinks"),
            {(e.errorCode, e.path) for e in result.errors},
        )
        review = {**draft, "status": "Review"}
        result = self.validator.validate(review, OBSERVATION_SCHEMA)
        self.assertIn(
            ("application_validation.source_links_required", "$.sourceLinks"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_observation_time_and_identity_field_boundaries(self) -> None:
        valid = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "observation-distinct-times-valid.json")
        self.assertNotEqual(valid["observedAt"], valid["createdAt"])
        self.assertValid(valid, OBSERVATION_SCHEMA)
        for name in [
            "observation-missing-observed-at-invalid.json",
            "observation-recorded-at-invalid.json",
            "observation-observation-id-invalid.json",
        ]:
            with self.subTest(name=name):
                self.assertInvalid(load_json(INVALID_KNOWLEDGE_CORE_FIXTURES / name), OBSERVATION_SCHEMA)

    def test_observation_schema_index_resolves_and_composes_application_rules(self) -> None:
        valid = load_json(VALID_KNOWLEDGE_CORE_FIXTURES / "observation-global-quantity-valid.json")
        self.assertValid({"observations": [valid]}, INDEX_SCHEMA)
        review_without_source = {**valid, "status": "Review"}
        result = self.validator.validate({"observations": [review_without_source]}, INDEX_SCHEMA)
        self.assertIn(
            (
                "application_validation.source_links_required",
                "$.observations[0].sourceLinks",
            ),
            {(e.errorCode, e.path) for e in result.errors},
        )
        invalid = load_json(
            INVALID_KNOWLEDGE_CORE_FIXTURES / "observation-negative-uncertainty-invalid.json"
        )
        result = self.validator.validate({"observations": [invalid]}, INDEX_SCHEMA)
        self.assertIn(
            (
                "application_validation.measurement_quality_negative_uncertainty",
                "$.observations[0].measurementQuality.uncertainty.value",
            ),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_unit_catalog_entry_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(UNIT_CATALOG_ENTRY_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_unit_catalog_fixtures_pass(self) -> None:
        files = sorted(VALID_CATALOG_FIXTURES.glob("unit-*-valid.json"))
        self.assertEqual(len(files), 8)
        for path in files:
            with self.subTest(path=path.name):
                self.assertValid(load_json(path), UNIT_CATALOG_ENTRY_SCHEMA)

    def test_invalid_unit_catalog_fixtures_fail(self) -> None:
        files = sorted(INVALID_CATALOG_FIXTURES.glob("unit-*-invalid.json"))
        self.assertEqual(len(files), 31)
        for path in files:
            with self.subTest(path=path.name):
                self.assertInvalid(load_json(path), UNIT_CATALOG_ENTRY_SCHEMA)

    def test_unit_catalog_entry_reuses_central_unt_and_common_metadata(self) -> None:
        schema = self.validator.registry.by_id[UNIT_CATALOG_ENTRY_SCHEMA]
        self.assertEqual(
            schema["properties"]["id"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/UNT",
        )
        metadata_fields = {
            "schemaVersion", "recordVersion", "revision", "status",
            "createdAt", "createdBy", "updatedAt", "updatedBy",
            "sourceLinks", "changeSummary", "notes",
        }
        for field in metadata_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    schema["properties"][field]["$ref"].startswith(
                        "https://eos.local/schemas/common/metadata.schema.json#/properties/"
                    )
                )

    def test_unit_catalog_entry_source_link_ref_resolves(self) -> None:
        valid = load_json(VALID_CATALOG_FIXTURES / "unit-source-links-valid.json")
        self.assertValid(valid, UNIT_CATALOG_ENTRY_SCHEMA)
        invalid = load_json(INVALID_CATALOG_FIXTURES / "unit-malformed-source-link-invalid.json")
        result = self.validator.validate(invalid, UNIT_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("schema_validation.required", "$.sourceLinks[0].verificationStatus"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_unit_catalog_entry_name_is_required_and_nonempty(self) -> None:
        cases = {
            "unit-missing-name-invalid.json": "schema_validation.required",
            "unit-empty-name-invalid.json": "schema_validation.minLength",
            "unit-name-wrong-type-invalid.json": "schema_validation.type",
        }
        for name, code in cases.items():
            with self.subTest(name=name):
                result = self.validator.validate(load_json(INVALID_CATALOG_FIXTURES / name), UNIT_CATALOG_ENTRY_SCHEMA)
                self.assertIn((code, "$.name"), {(e.errorCode, e.path) for e in result.errors})

    def test_unit_catalog_entry_symbol_is_required_and_nonempty(self) -> None:
        cases = {
            "unit-missing-symbol-invalid.json": "schema_validation.required",
            "unit-empty-symbol-invalid.json": "schema_validation.minLength",
            "unit-symbol-wrong-type-invalid.json": "schema_validation.type",
        }
        for name, code in cases.items():
            with self.subTest(name=name):
                result = self.validator.validate(load_json(INVALID_CATALOG_FIXTURES / name), UNIT_CATALOG_ENTRY_SCHEMA)
                self.assertIn((code, "$.symbol"), {(e.errorCode, e.path) for e in result.errors})

    def test_unit_catalog_entry_symbol_is_not_identity_or_structurally_unique(self) -> None:
        first = load_json(VALID_CATALOG_FIXTURES / "unit-minimal-draft-valid.json")
        second = load_json(VALID_CATALOG_FIXTURES / "unit-duplicate-symbol-valid.json")
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(first["symbol"], second["symbol"])
        self.assertValid({"unitCatalogEntries": [first, second]}, INDEX_SCHEMA)

    def test_unit_catalog_entry_optional_description_and_notes(self) -> None:
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "unit-description-valid.json"),
            UNIT_CATALOG_ENTRY_SCHEMA,
        )
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "unit-notes-valid.json"),
            UNIT_CATALOG_ENTRY_SCHEMA,
        )

    def test_unit_catalog_entry_replacement_links_use_unt(self) -> None:
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "unit-replaces-valid.json"),
            UNIT_CATALOG_ENTRY_SCHEMA,
        )
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "unit-replaced-by-valid.json"),
            UNIT_CATALOG_ENTRY_SCHEMA,
        )
        for name, path in [
            ("unit-invalid-replaces-invalid.json", "$.replaces"),
            ("unit-invalid-replaced-by-invalid.json", "$.replacedBy"),
        ]:
            with self.subTest(name=name):
                result = self.validator.validate(load_json(INVALID_CATALOG_FIXTURES / name), UNIT_CATALOG_ENTRY_SCHEMA)
                self.assertIn(
                    ("schema_validation.pattern", path),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_unit_catalog_entry_rejects_deferred_fields(self) -> None:
        base = load_json(VALID_CATALOG_FIXTURES / "unit-minimal-draft-valid.json")
        fields = {
            "quantityKind": "fictional",
            "quantityKindId": "fictional",
            "dimension": "fictional",
            "dimensionSignature": {},
            "system": "fictional",
            "unitSystem": "fictional",
            "aliases": ["fictional"],
            "conversion": {},
            "baseUnitId": "UNT-900002",
            "scale": 2,
            "offset": 2,
            "conversionFactor": 2,
            "isSI": False,
            "canonicalBaseUnit": "UNT-900002",
            "equivalence": [],
            "formula": "fictional",
            "expression": "fictional",
        }
        for field, value in fields.items():
            with self.subTest(field=field):
                result = self.validator.validate({**base, field: value}, UNIT_CATALOG_ENTRY_SCHEMA)
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field}"),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_unit_catalog_entry_rejects_root_verification_status_and_unit_id(self) -> None:
        base = load_json(VALID_CATALOG_FIXTURES / "unit-minimal-draft-valid.json")
        for field, value in {
            "verificationStatus": "Approved",
            "unitId": "UNT-900001",
        }.items():
            with self.subTest(field=field):
                result = self.validator.validate({**base, field: value}, UNIT_CATALOG_ENTRY_SCHEMA)
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field}"),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_unit_catalog_entry_lifecycle_uses_record_status(self) -> None:
        draft = load_json(VALID_CATALOG_FIXTURES / "unit-minimal-draft-valid.json")
        sourced = load_json(VALID_CATALOG_FIXTURES / "unit-source-links-valid.json")["sourceLinks"]
        for status in ["Draft", "Review", "Approved", "Deprecated", "Archived"]:
            with self.subTest(status=status):
                record = {**draft, "status": status}
                if status in {"Review", "Approved"}:
                    record["sourceLinks"] = sourced
                self.assertValid(record, UNIT_CATALOG_ENTRY_SCHEMA)
        self.assertInvalid({**draft, "status": "Active"}, UNIT_CATALOG_ENTRY_SCHEMA)

    def test_unit_catalog_entry_source_lifecycle_rule_is_composed(self) -> None:
        draft = load_json(VALID_CATALOG_FIXTURES / "unit-minimal-draft-valid.json")
        self.assertValid(draft, UNIT_CATALOG_ENTRY_SCHEMA)
        review = {**draft, "status": "Review"}
        direct = self.validator.validate(review, UNIT_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("application_validation.source_links_required", "$.sourceLinks"),
            {(e.errorCode, e.path) for e in direct.errors},
        )
        nested = self.validator.validate({"unitCatalogEntries": [review]}, INDEX_SCHEMA)
        self.assertIn(
            ("application_validation.source_links_required", "$.unitCatalogEntries[0].sourceLinks"),
            {(e.errorCode, e.path) for e in nested.errors},
        )

    def test_schema_index_resolves_unit_catalog_entry(self) -> None:
        schema = self.validator.registry.by_id[INDEX_SCHEMA]
        self.assertEqual(
            schema["$defs"]["unitCatalogEntry"]["$ref"],
            UNIT_CATALOG_ENTRY_SCHEMA,
        )
        valid = load_json(VALID_CATALOG_FIXTURES / "unit-minimal-draft-valid.json")
        self.assertValid({"unitCatalogEntries": [valid]}, INDEX_SCHEMA)

    def test_condition_type_catalog_entry_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_condition_type_catalog_fixtures_pass(self) -> None:
        files = sorted(VALID_CATALOG_FIXTURES.glob("condition-type-*-valid.json"))
        self.assertEqual(len(files), 8)
        for path in files:
            with self.subTest(path=path.name):
                self.assertValid(load_json(path), CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)

    def test_invalid_condition_type_catalog_fixtures_fail(self) -> None:
        files = sorted(INVALID_CATALOG_FIXTURES.glob("condition-type-*-invalid.json"))
        self.assertEqual(len(files), 38)
        for path in files:
            with self.subTest(path=path.name):
                self.assertInvalid(load_json(path), CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)

    def test_condition_type_catalog_reuses_central_cnd_and_common_metadata(self) -> None:
        schema = self.validator.registry.by_id[CONDITION_TYPE_CATALOG_ENTRY_SCHEMA]
        self.assertEqual(
            schema["properties"]["id"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/CND",
        )
        metadata_fields = {
            "schemaVersion", "recordVersion", "revision", "status",
            "createdAt", "createdBy", "updatedAt", "updatedBy",
            "sourceLinks", "changeSummary", "notes",
        }
        for field in metadata_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    schema["properties"][field]["$ref"].startswith(
                        "https://eos.local/schemas/common/metadata.schema.json#/properties/"
                    )
                )

    def test_condition_type_catalog_source_link_ref_resolves(self) -> None:
        valid = load_json(VALID_CATALOG_FIXTURES / "condition-type-source-links-valid.json")
        self.assertValid(valid, CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)
        invalid = load_json(INVALID_CATALOG_FIXTURES / "condition-type-malformed-source-link-invalid.json")
        result = self.validator.validate(invalid, CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("schema_validation.required", "$.sourceLinks[0].verificationStatus"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_condition_type_catalog_name_is_required_and_nonempty(self) -> None:
        cases = {
            "condition-type-missing-name-invalid.json": "schema_validation.required",
            "condition-type-empty-name-invalid.json": "schema_validation.minLength",
            "condition-type-name-wrong-type-invalid.json": "schema_validation.type",
        }
        for name, code in cases.items():
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_CATALOG_FIXTURES / name),
                    CONDITION_TYPE_CATALOG_ENTRY_SCHEMA,
                )
                self.assertIn((code, "$.name"), {(e.errorCode, e.path) for e in result.errors})

    def test_condition_type_catalog_allowed_value_forms_are_closed_and_unique(self) -> None:
        schema = self.validator.registry.by_id[CONDITION_TYPE_CATALOG_ENTRY_SCHEMA]
        value_forms = schema["properties"]["allowedValueForms"]
        self.assertEqual(
            set(value_forms["items"]["enum"]),
            {"quantity", "valueRange", "textValue", "booleanValue", "referenceId"},
        )
        self.assertEqual(value_forms["minItems"], 1)
        self.assertTrue(value_forms["uniqueItems"])
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "condition-type-multiple-value-forms-valid.json"),
            CONDITION_TYPE_CATALOG_ENTRY_SCHEMA,
        )
        cases = {
            "condition-type-missing-allowed-value-forms-invalid.json": "schema_validation.required",
            "condition-type-empty-allowed-value-forms-invalid.json": "schema_validation.minItems",
            "condition-type-unsupported-value-form-invalid.json": "schema_validation.enum",
            "condition-type-duplicate-value-form-invalid.json": "schema_validation.uniqueItems",
            "condition-type-allowed-value-forms-wrong-type-invalid.json": "schema_validation.type",
        }
        for name, code in cases.items():
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_CATALOG_FIXTURES / name),
                    CONDITION_TYPE_CATALOG_ENTRY_SCHEMA,
                )
                self.assertTrue(any(error.errorCode == code for error in result.errors), name)

    def test_condition_type_catalog_reference_policy_matches_condition_union(self) -> None:
        catalog_schema = self.validator.registry.by_id[CONDITION_TYPE_CATALOG_ENTRY_SCHEMA]
        condition_schema = self.validator.registry.by_id[CONDITION_SCHEMA]
        catalog_families = set(
            catalog_schema["properties"]["allowedReferencePrefixes"]["items"]["enum"]
        )
        condition_families = {
            item["$ref"].rsplit("/", 1)[-1]
            for item in condition_schema["properties"]["referenceId"]["anyOf"]
        }
        self.assertEqual(catalog_families, condition_families)

        valid = load_json(VALID_CATALOG_FIXTURES / "condition-type-multiple-value-forms-valid.json")
        self.assertValid(valid, CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)
        for name in [
            "condition-type-reference-missing-prefixes-invalid.json",
            "condition-type-prefixes-without-reference-invalid.json",
            "condition-type-empty-reference-prefixes-invalid.json",
            "condition-type-unsupported-reference-prefix-invalid.json",
            "condition-type-duplicate-reference-prefix-invalid.json",
            "condition-type-reference-prefixes-wrong-type-invalid.json",
        ]:
            with self.subTest(name=name):
                self.assertInvalid(
                    load_json(INVALID_CATALOG_FIXTURES / name),
                    CONDITION_TYPE_CATALOG_ENTRY_SCHEMA,
                )

    def test_condition_type_catalog_rejects_deferred_semantics(self) -> None:
        base = load_json(VALID_CATALOG_FIXTURES / "condition-type-minimal-draft-valid.json")
        fields = {
            "allowedEvaluationModes": ["contextual"],
            "defaultEvaluationMode": "contextual",
            "fixedEvaluationMode": "contextual",
            "allowedUnitIds": ["UNT-900001"],
            "requiredUnitId": "UNT-900001",
            "quantityKind": "fictional",
            "dimension": "fictional",
            "allowMultiple": True,
            "uniquenessScope": "fictional",
            "logicalOperator": "AND",
            "allowedReferenceTypes": ["SourceReference"],
            "aliases": ["fictional"],
            "verificationStatus": "Approved",
        }
        for field, value in fields.items():
            with self.subTest(field=field):
                result = self.validator.validate(
                    {**base, field: value},
                    CONDITION_TYPE_CATALOG_ENTRY_SCHEMA,
                )
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field}"),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_condition_type_catalog_replacement_links_use_cnd(self) -> None:
        for name in ["condition-type-replaces-valid.json", "condition-type-replaced-by-valid.json"]:
            with self.subTest(name=name):
                self.assertValid(
                    load_json(VALID_CATALOG_FIXTURES / name),
                    CONDITION_TYPE_CATALOG_ENTRY_SCHEMA,
                )
        for name, path in [
            ("condition-type-invalid-replaces-invalid.json", "$.replaces"),
            ("condition-type-invalid-replaced-by-invalid.json", "$.replacedBy"),
        ]:
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_CATALOG_FIXTURES / name),
                    CONDITION_TYPE_CATALOG_ENTRY_SCHEMA,
                )
                self.assertIn(
                    ("schema_validation.pattern", path),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_condition_type_catalog_lifecycle_uses_record_status(self) -> None:
        draft = load_json(VALID_CATALOG_FIXTURES / "condition-type-minimal-draft-valid.json")
        sourced = load_json(VALID_CATALOG_FIXTURES / "condition-type-source-links-valid.json")["sourceLinks"]
        for status in ["Draft", "Review", "Approved", "Deprecated", "Archived"]:
            with self.subTest(status=status):
                record = {**draft, "status": status}
                if status in {"Review", "Approved"}:
                    record["sourceLinks"] = sourced
                self.assertValid(record, CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)
        self.assertInvalid({**draft, "status": "Active"}, CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)

    def test_condition_type_catalog_source_lifecycle_rule_is_composed(self) -> None:
        draft = load_json(VALID_CATALOG_FIXTURES / "condition-type-minimal-draft-valid.json")
        self.assertValid(draft, CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)
        review = {**draft, "status": "Review"}
        direct = self.validator.validate(review, CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("application_validation.source_links_required", "$.sourceLinks"),
            {(e.errorCode, e.path) for e in direct.errors},
        )
        nested = self.validator.validate({"conditionTypeCatalogEntries": [review]}, INDEX_SCHEMA)
        self.assertIn(
            (
                "application_validation.source_links_required",
                "$.conditionTypeCatalogEntries[0].sourceLinks",
            ),
            {(e.errorCode, e.path) for e in nested.errors},
        )

    def test_condition_type_catalog_rejects_unknown_root_fields(self) -> None:
        record = load_json(INVALID_CATALOG_FIXTURES / "condition-type-unknown-root-field-invalid.json")
        result = self.validator.validate(record, CONDITION_TYPE_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("schema_validation.additionalProperties", "$.fictionalField"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_schema_index_resolves_condition_type_catalog_entry(self) -> None:
        schema = self.validator.registry.by_id[INDEX_SCHEMA]
        self.assertEqual(
            schema["$defs"]["conditionTypeCatalogEntry"]["$ref"],
            CONDITION_TYPE_CATALOG_ENTRY_SCHEMA,
        )
        valid = load_json(VALID_CATALOG_FIXTURES / "condition-type-minimal-draft-valid.json")
        self.assertValid({"conditionTypeCatalogEntries": [valid]}, INDEX_SCHEMA)

    def test_condition_type_catalog_does_not_validate_condition_instances_yet(self) -> None:
        condition = {
            "conditionTypeId": "CND-999999",
            "evaluationMode": "contextual",
            "textValue": "fictional context",
        }
        result = self.validator.validate(condition, CONDITION_SCHEMA)
        self.assertTrue(result.ok, [f"{e.errorCode}: {e.message}" for e in result.errors])

    def test_property_catalog_entry_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(PROPERTY_CATALOG_ENTRY_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_property_catalog_fixtures_pass(self) -> None:
        files = sorted(VALID_CATALOG_FIXTURES.glob("property-*-valid.json"))
        self.assertEqual(len(files), 11)
        for path in files:
            with self.subTest(path=path.name):
                self.assertValid(load_json(path), PROPERTY_CATALOG_ENTRY_SCHEMA)

    def test_invalid_property_catalog_fixtures_fail(self) -> None:
        files = sorted(INVALID_CATALOG_FIXTURES.glob("property-*-invalid.json"))
        self.assertEqual(len(files), 44)
        for path in files:
            with self.subTest(path=path.name):
                self.assertInvalid(load_json(path), PROPERTY_CATALOG_ENTRY_SCHEMA)

    def test_property_catalog_reuses_central_ids_and_common_metadata(self) -> None:
        schema = self.validator.registry.by_id[PROPERTY_CATALOG_ENTRY_SCHEMA]
        identifiers = {
            "id": "PRP",
            "replaces": "PRP",
            "replacedBy": "PRP",
        }
        for field, identifier in identifiers.items():
            with self.subTest(field=field):
                self.assertEqual(
                    schema["properties"][field]["$ref"],
                    f"https://eos.local/schemas/common/identifiers.schema.json#/$defs/{identifier}",
                )
        for field in {
            "schemaVersion", "recordVersion", "revision", "status",
            "createdAt", "createdBy", "updatedAt", "updatedBy",
            "sourceLinks", "changeSummary", "notes",
        }:
            with self.subTest(field=field):
                self.assertTrue(
                    schema["properties"][field]["$ref"].startswith(
                        "https://eos.local/schemas/common/metadata.schema.json#/properties/"
                    )
                )

    def test_property_catalog_source_link_ref_resolves(self) -> None:
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "property-source-links-valid.json"),
            PROPERTY_CATALOG_ENTRY_SCHEMA,
        )
        invalid = load_json(INVALID_CATALOG_FIXTURES / "property-malformed-source-link-invalid.json")
        result = self.validator.validate(invalid, PROPERTY_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("schema_validation.required", "$.sourceLinks[0].verificationStatus"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_property_catalog_name_and_description_are_required_and_nonempty(self) -> None:
        cases = {
            "property-missing-name-invalid.json": ("schema_validation.required", "$.name"),
            "property-empty-name-invalid.json": ("schema_validation.minLength", "$.name"),
            "property-name-wrong-type-invalid.json": ("schema_validation.type", "$.name"),
            "property-missing-description-invalid.json": ("schema_validation.required", "$.description"),
            "property-empty-description-invalid.json": ("schema_validation.minLength", "$.description"),
            "property-description-wrong-type-invalid.json": ("schema_validation.type", "$.description"),
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_CATALOG_FIXTURES / name),
                    PROPERTY_CATALOG_ENTRY_SCHEMA,
                )
                self.assertIn(expected, {(e.errorCode, e.path) for e in result.errors})

    def test_property_catalog_allowed_value_types_are_closed_nonempty_and_unique(self) -> None:
        schema = self.validator.registry.by_id[PROPERTY_CATALOG_ENTRY_SCHEMA]
        field = schema["properties"]["allowedValueTypes"]
        self.assertEqual(set(field["items"]["enum"]), {"quantity", "valueRange"})
        self.assertEqual(field["minItems"], 1)
        self.assertTrue(field["uniqueItems"])
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "property-both-value-types-valid.json"),
            PROPERTY_CATALOG_ENTRY_SCHEMA,
        )
        for name in [
            "property-missing-allowed-value-types-invalid.json",
            "property-empty-allowed-value-types-invalid.json",
            "property-unsupported-allowed-value-type-invalid.json",
            "property-duplicate-allowed-value-types-invalid.json",
            "property-allowed-value-types-wrong-type-invalid.json",
        ]:
            with self.subTest(name=name):
                self.assertInvalid(load_json(INVALID_CATALOG_FIXTURES / name), PROPERTY_CATALOG_ENTRY_SCHEMA)

    def test_property_catalog_allowed_unit_ids_are_required_nonempty_unique_unt_refs(self) -> None:
        schema = self.validator.registry.by_id[PROPERTY_CATALOG_ENTRY_SCHEMA]
        field = schema["properties"]["allowedUnitIds"]
        self.assertEqual(field["minItems"], 1)
        self.assertTrue(field["uniqueItems"])
        self.assertEqual(
            field["items"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/UNT",
        )
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "property-multiple-units-valid.json"),
            PROPERTY_CATALOG_ENTRY_SCHEMA,
        )
        for name in [
            "property-missing-allowed-unit-ids-invalid.json",
            "property-empty-allowed-unit-ids-invalid.json",
            "property-invalid-unit-id-invalid.json",
            "property-duplicate-allowed-unit-ids-invalid.json",
            "property-allowed-unit-ids-wrong-type-invalid.json",
        ]:
            with self.subTest(name=name):
                self.assertInvalid(load_json(INVALID_CATALOG_FIXTURES / name), PROPERTY_CATALOG_ENTRY_SCHEMA)

    def test_property_catalog_condition_allowlist_is_optional_nonempty_unique_cnd_refs(self) -> None:
        schema = self.validator.registry.by_id[PROPERTY_CATALOG_ENTRY_SCHEMA]
        field = schema["properties"]["allowedConditionTypeIds"]
        self.assertNotIn("allowedConditionTypeIds", schema["required"])
        self.assertEqual(field["minItems"], 1)
        self.assertTrue(field["uniqueItems"])
        self.assertEqual(
            field["items"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/CND",
        )
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "property-minimal-draft-valid.json"),
            PROPERTY_CATALOG_ENTRY_SCHEMA,
        )
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "property-conditions-valid.json"),
            PROPERTY_CATALOG_ENTRY_SCHEMA,
        )
        for name in [
            "property-empty-allowed-condition-type-ids-invalid.json",
            "property-invalid-condition-type-id-invalid.json",
            "property-duplicate-allowed-condition-type-ids-invalid.json",
            "property-allowed-condition-type-ids-wrong-type-invalid.json",
        ]:
            with self.subTest(name=name):
                self.assertInvalid(load_json(INVALID_CATALOG_FIXTURES / name), PROPERTY_CATALOG_ENTRY_SCHEMA)

    def test_property_catalog_rejects_deferred_semantics_and_verification_status(self) -> None:
        base = load_json(VALID_CATALOG_FIXTURES / "property-minimal-draft-valid.json")
        fields = {
            "verificationStatus": "Approved",
            "canonicalUnitId": "UNT-900001",
            "requiredConditionTypeIds": ["CND-910001"],
            "classifications": [],
            "aliases": ["Fictional alias"],
            "quantityKind": "fictional",
            "dimension": "fictional",
            "conversion": {},
        }
        for field, value in fields.items():
            with self.subTest(field=field):
                result = self.validator.validate({**base, field: value}, PROPERTY_CATALOG_ENTRY_SCHEMA)
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field}"),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_property_catalog_replacement_links_use_prp(self) -> None:
        for name in ["property-replaces-valid.json", "property-replaced-by-valid.json"]:
            with self.subTest(name=name):
                self.assertValid(load_json(VALID_CATALOG_FIXTURES / name), PROPERTY_CATALOG_ENTRY_SCHEMA)
        for name, path in [
            ("property-invalid-replaces-invalid.json", "$.replaces"),
            ("property-invalid-replaced-by-invalid.json", "$.replacedBy"),
        ]:
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_CATALOG_FIXTURES / name),
                    PROPERTY_CATALOG_ENTRY_SCHEMA,
                )
                self.assertIn(
                    ("schema_validation.pattern", path),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_property_catalog_lifecycle_uses_record_status(self) -> None:
        draft = load_json(VALID_CATALOG_FIXTURES / "property-minimal-draft-valid.json")
        sourced = load_json(VALID_CATALOG_FIXTURES / "property-source-links-valid.json")["sourceLinks"]
        for status in ["Draft", "Review", "Approved", "Deprecated", "Archived"]:
            with self.subTest(status=status):
                record = {**draft, "status": status}
                if status in {"Review", "Approved"}:
                    record["sourceLinks"] = sourced
                self.assertValid(record, PROPERTY_CATALOG_ENTRY_SCHEMA)
        self.assertInvalid({**draft, "status": "Active"}, PROPERTY_CATALOG_ENTRY_SCHEMA)

    def test_property_catalog_source_lifecycle_rule_is_composed(self) -> None:
        draft = load_json(VALID_CATALOG_FIXTURES / "property-minimal-draft-valid.json")
        self.assertValid(draft, PROPERTY_CATALOG_ENTRY_SCHEMA)
        review = {**draft, "status": "Review"}
        direct = self.validator.validate(review, PROPERTY_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("application_validation.source_links_required", "$.sourceLinks"),
            {(e.errorCode, e.path) for e in direct.errors},
        )
        nested = self.validator.validate({"propertyCatalogEntries": [review]}, INDEX_SCHEMA)
        self.assertIn(
            ("application_validation.source_links_required", "$.propertyCatalogEntries[0].sourceLinks"),
            {(e.errorCode, e.path) for e in nested.errors},
        )

    def test_property_catalog_rejects_unknown_root_fields(self) -> None:
        record = load_json(INVALID_CATALOG_FIXTURES / "property-unknown-root-field-invalid.json")
        result = self.validator.validate(record, PROPERTY_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("schema_validation.additionalProperties", "$.fictionalField"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_schema_index_resolves_property_catalog_entry(self) -> None:
        schema = self.validator.registry.by_id[INDEX_SCHEMA]
        self.assertEqual(
            schema["$defs"]["propertyCatalogEntry"]["$ref"],
            PROPERTY_CATALOG_ENTRY_SCHEMA,
        )
        valid = load_json(VALID_CATALOG_FIXTURES / "property-minimal-draft-valid.json")
        self.assertValid({"propertyCatalogEntries": [valid]}, INDEX_SCHEMA)

    def test_property_catalog_does_not_validate_consumers_yet(self) -> None:
        property_record = load_json(
            VALID_KNOWLEDGE_CORE_FIXTURES / "property-record-quantity-valid.json"
        )
        property_record["propertyId"] = "PRP-999999"
        property_record["quantity"]["unitId"] = "UNT-999999"
        self.assertValid(property_record, PROPERTY_RECORD_SCHEMA)

        observation = load_json(
            VALID_KNOWLEDGE_CORE_FIXTURES / "observation-global-quantity-valid.json"
        )
        observation["propertyId"] = "PRP-999999"
        observation["quantity"]["unitId"] = "UNT-999999"
        self.assertValid(observation, OBSERVATION_SCHEMA)

    def test_classification_catalog_entry_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
        self.assertTrue(result.ok, [f"{e.schemaPath}: {e.message}" for e in result.errors])

    def test_valid_classification_catalog_fixtures_pass(self) -> None:
        files = sorted(VALID_CATALOG_FIXTURES.glob("classification-catalog-*-valid.json"))
        self.assertEqual(len(files), 9)
        for path in files:
            with self.subTest(path=path.name):
                self.assertValid(load_json(path), CLASSIFICATION_CATALOG_ENTRY_SCHEMA)

    def test_invalid_classification_catalog_fixtures_fail(self) -> None:
        cases = {
            "classification-catalog-empty-object-invalid.json": ("schema_validation.required", "$.id"),
            "classification-catalog-missing-id-invalid.json": ("schema_validation.required", "$.id"),
            "classification-catalog-invalid-cls-prefix-invalid.json": ("schema_validation.pattern", "$.id"),
            "classification-catalog-lowercase-cls-invalid.json": ("schema_validation.pattern", "$.id"),
            "classification-catalog-incomplete-cls-padding-invalid.json": ("schema_validation.pattern", "$.id"),
            "classification-catalog-missing-name-invalid.json": ("schema_validation.required", "$.name"),
            "classification-catalog-empty-name-invalid.json": ("schema_validation.minLength", "$.name"),
            "classification-catalog-name-wrong-type-invalid.json": ("schema_validation.type", "$.name"),
            "classification-catalog-missing-description-invalid.json": ("schema_validation.required", "$.description"),
            "classification-catalog-empty-description-invalid.json": ("schema_validation.minLength", "$.description"),
            "classification-catalog-description-wrong-type-invalid.json": ("schema_validation.type", "$.description"),
            "classification-catalog-missing-source-links-invalid.json": ("schema_validation.required", "$.sourceLinks"),
            "classification-catalog-malformed-source-link-invalid.json": ("schema_validation.required", "$.sourceLinks[0].verificationStatus"),
            "classification-catalog-source-links-wrong-type-invalid.json": ("schema_validation.type", "$.sourceLinks"),
            "classification-catalog-verification-status-invalid.json": ("schema_validation.additionalProperties", "$.verificationStatus"),
            "classification-catalog-classification-system-invalid.json": ("schema_validation.additionalProperties", "$.classificationSystem"),
            "classification-catalog-classification-system-id-invalid.json": ("schema_validation.additionalProperties", "$.classificationSystemId"),
            "classification-catalog-external-code-invalid.json": ("schema_validation.additionalProperties", "$.externalCode"),
            "classification-catalog-parent-id-invalid.json": ("schema_validation.additionalProperties", "$.parentId"),
            "classification-catalog-parent-ids-invalid.json": ("schema_validation.additionalProperties", "$.parentIds"),
            "classification-catalog-hierarchy-path-invalid.json": ("schema_validation.additionalProperties", "$.hierarchyPath"),
            "classification-catalog-level-invalid.json": ("schema_validation.additionalProperties", "$.level"),
            "classification-catalog-aliases-invalid.json": ("schema_validation.additionalProperties", "$.aliases"),
            "classification-catalog-equivalent-to-invalid.json": ("schema_validation.additionalProperties", "$.equivalentTo"),
            "classification-catalog-broader-than-invalid.json": ("schema_validation.additionalProperties", "$.broaderThan"),
            "classification-catalog-narrower-than-invalid.json": ("schema_validation.additionalProperties", "$.narrowerThan"),
            "classification-catalog-allowed-target-types-invalid.json": ("schema_validation.additionalProperties", "$.allowedTargetTypes"),
            "classification-catalog-unknown-root-field-invalid.json": ("schema_validation.additionalProperties", "$.fictionalField"),
            "classification-catalog-invalid-replaces-invalid.json": ("schema_validation.pattern", "$.replaces"),
            "classification-catalog-invalid-replaced-by-invalid.json": ("schema_validation.pattern", "$.replacedBy"),
            "classification-catalog-null-id-invalid.json": ("schema_validation.type", "$.id"),
            "classification-catalog-null-name-invalid.json": ("schema_validation.type", "$.name"),
            "classification-catalog-null-description-invalid.json": ("schema_validation.type", "$.description"),
            "classification-catalog-array-instead-of-object-invalid.json": ("schema_validation.type", "$"),
        }
        files = sorted(INVALID_CATALOG_FIXTURES.glob("classification-catalog-*-invalid.json"))
        self.assertEqual(len(files), 34)
        self.assertEqual({path.name for path in files}, set(cases))
        for path in files:
            with self.subTest(path=path.name):
                result = self.validator.validate(load_json(path), CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
                self.assertIn(cases[path.name], {(e.errorCode, e.path) for e in result.errors})

    def test_classification_catalog_reuses_central_cls_and_common_metadata(self) -> None:
        schema = self.validator.registry.by_id[CLASSIFICATION_CATALOG_ENTRY_SCHEMA]
        for field in {"id", "replaces", "replacedBy"}:
            with self.subTest(field=field):
                self.assertEqual(
                    schema["properties"][field]["$ref"],
                    "https://eos.local/schemas/common/identifiers.schema.json#/$defs/CLS",
                )
        for field in {
            "schemaVersion", "recordVersion", "revision", "status",
            "createdAt", "createdBy", "updatedAt", "updatedBy",
            "sourceLinks", "changeSummary", "notes",
        }:
            with self.subTest(field=field):
                self.assertTrue(
                    schema["properties"][field]["$ref"].startswith(
                        "https://eos.local/schemas/common/metadata.schema.json#/properties/"
                    )
                )

    def test_classification_catalog_source_link_ref_resolves(self) -> None:
        self.assertValid(
            load_json(VALID_CATALOG_FIXTURES / "classification-catalog-source-links-valid.json"),
            CLASSIFICATION_CATALOG_ENTRY_SCHEMA,
        )
        invalid = load_json(
            INVALID_CATALOG_FIXTURES / "classification-catalog-malformed-source-link-invalid.json"
        )
        result = self.validator.validate(invalid, CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("schema_validation.required", "$.sourceLinks[0].verificationStatus"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_classification_catalog_name_and_description_are_required_and_nonempty(self) -> None:
        cases = {
            "classification-catalog-missing-name-invalid.json": ("schema_validation.required", "$.name"),
            "classification-catalog-empty-name-invalid.json": ("schema_validation.minLength", "$.name"),
            "classification-catalog-name-wrong-type-invalid.json": ("schema_validation.type", "$.name"),
            "classification-catalog-missing-description-invalid.json": ("schema_validation.required", "$.description"),
            "classification-catalog-empty-description-invalid.json": ("schema_validation.minLength", "$.description"),
            "classification-catalog-description-wrong-type-invalid.json": ("schema_validation.type", "$.description"),
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_CATALOG_FIXTURES / name),
                    CLASSIFICATION_CATALOG_ENTRY_SCHEMA,
                )
                self.assertIn(expected, {(e.errorCode, e.path) for e in result.errors})

    def test_classification_catalog_name_is_not_identity_or_structurally_unique(self) -> None:
        first = load_json(VALID_CATALOG_FIXTURES / "classification-catalog-duplicate-name-a-valid.json")
        second = load_json(VALID_CATALOG_FIXTURES / "classification-catalog-duplicate-name-b-valid.json")
        self.assertEqual(first["name"], second["name"])
        self.assertNotEqual(first["id"], second["id"])
        self.assertValid(first, CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
        self.assertValid(second, CLASSIFICATION_CATALOG_ENTRY_SCHEMA)

    def test_classification_catalog_rejects_deferred_semantics_and_verification_status(self) -> None:
        fields = {
            "verificationStatus": "verification-status",
            "classificationSystem": "classification-system",
            "classificationSystemId": "classification-system-id",
            "externalCode": "external-code",
            "parentId": "parent-id",
            "parentIds": "parent-ids",
            "hierarchyPath": "hierarchy-path",
            "level": "level",
            "aliases": "aliases",
            "equivalentTo": "equivalent-to",
            "broaderThan": "broader-than",
            "narrowerThan": "narrower-than",
            "allowedTargetTypes": "allowed-target-types",
        }
        for field, filename in fields.items():
            path = INVALID_CATALOG_FIXTURES / f"classification-catalog-{filename}-invalid.json"
            with self.subTest(field=field):
                result = self.validator.validate(load_json(path), CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field}"),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_classification_catalog_replacement_links_use_cls(self) -> None:
        for name in [
            "classification-catalog-replaces-valid.json",
            "classification-catalog-replaced-by-valid.json",
        ]:
            with self.subTest(name=name):
                self.assertValid(load_json(VALID_CATALOG_FIXTURES / name), CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
        for name, path in [
            ("classification-catalog-invalid-replaces-invalid.json", "$.replaces"),
            ("classification-catalog-invalid-replaced-by-invalid.json", "$.replacedBy"),
        ]:
            with self.subTest(name=name):
                result = self.validator.validate(
                    load_json(INVALID_CATALOG_FIXTURES / name),
                    CLASSIFICATION_CATALOG_ENTRY_SCHEMA,
                )
                self.assertIn(
                    ("schema_validation.pattern", path),
                    {(e.errorCode, e.path) for e in result.errors},
                )

    def test_classification_catalog_lifecycle_uses_record_status(self) -> None:
        draft = load_json(VALID_CATALOG_FIXTURES / "classification-catalog-minimal-draft-valid.json")
        sourced = load_json(
            VALID_CATALOG_FIXTURES / "classification-catalog-source-links-valid.json"
        )["sourceLinks"]
        for status in ["Draft", "Review", "Approved", "Deprecated", "Archived"]:
            with self.subTest(status=status):
                record = {**draft, "status": status}
                if status in {"Review", "Approved"}:
                    record["sourceLinks"] = sourced
                self.assertValid(record, CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
        self.assertInvalid({**draft, "status": "Active"}, CLASSIFICATION_CATALOG_ENTRY_SCHEMA)

    def test_classification_catalog_source_lifecycle_rule_is_composed(self) -> None:
        draft = load_json(VALID_CATALOG_FIXTURES / "classification-catalog-minimal-draft-valid.json")
        self.assertValid(draft, CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
        review = {**draft, "status": "Review"}
        direct = self.validator.validate(review, CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("application_validation.source_links_required", "$.sourceLinks"),
            {(e.errorCode, e.path) for e in direct.errors},
        )
        nested = self.validator.validate({"classificationCatalogEntries": [review]}, INDEX_SCHEMA)
        self.assertIn(
            ("application_validation.source_links_required", "$.classificationCatalogEntries[0].sourceLinks"),
            {(e.errorCode, e.path) for e in nested.errors},
        )

    def test_classification_catalog_rejects_unknown_root_fields(self) -> None:
        record = load_json(
            INVALID_CATALOG_FIXTURES / "classification-catalog-unknown-root-field-invalid.json"
        )
        result = self.validator.validate(record, CLASSIFICATION_CATALOG_ENTRY_SCHEMA)
        self.assertIn(
            ("schema_validation.additionalProperties", "$.fictionalField"),
            {(e.errorCode, e.path) for e in result.errors},
        )

    def test_schema_index_resolves_classification_catalog_entry(self) -> None:
        schema = self.validator.registry.by_id[INDEX_SCHEMA]
        self.assertEqual(
            schema["$defs"]["classificationCatalogEntry"]["$ref"],
            CLASSIFICATION_CATALOG_ENTRY_SCHEMA,
        )
        valid = load_json(
            VALID_CATALOG_FIXTURES / "classification-catalog-minimal-draft-valid.json"
        )
        self.assertValid({"classificationCatalogEntries": [valid]}, INDEX_SCHEMA)

    def test_classification_catalog_does_not_validate_assignments_yet(self) -> None:
        classification = {
            "classificationId": "CLS-999999",
            "sourceLinks": [],
        }
        self.assertValid(classification, CLASSIFICATION_SCHEMA)

    def test_material_schema_definition_is_valid(self) -> None:
        result = self.validator.validate_schema_definition(MATERIAL_SCHEMA)
        self.assertTrue(result.ok, [(error.path, error.message) for error in result.errors])

    def test_valid_material_fixtures_pass(self) -> None:
        fixtures = sorted(VALID_ENTITY_FIXTURES.glob("material-*-valid.json"))
        self.assertEqual(len(fixtures), 16)
        for fixture in fixtures:
            with self.subTest(fixture=fixture.name):
                result = self.validator.validate_json_file(fixture, MATERIAL_SCHEMA)
                self.assertTrue(result.ok, [(error.path, error.message) for error in result.errors])

    def test_invalid_material_fixtures_fail(self) -> None:
        fixtures = sorted(INVALID_ENTITY_FIXTURES.glob("material-*-invalid.json"))
        self.assertEqual(len(fixtures), 42)
        for fixture in fixtures:
            with self.subTest(fixture=fixture.name):
                result = self.validator.validate_json_file(fixture, MATERIAL_SCHEMA)
                self.assertFalse(result.ok, fixture.name)

    def test_material_reuses_central_mat_and_common_metadata(self) -> None:
        schema = self.validator.registry.by_id[MATERIAL_SCHEMA]
        self.assertEqual(
            schema["properties"]["id"]["$ref"],
            "https://eos.local/schemas/common/identifiers.schema.json#/$defs/MAT",
        )
        self.assertNotIn("pattern", schema["properties"]["id"])
        for field_name in [
            "schemaVersion",
            "recordVersion",
            "revision",
            "status",
            "createdAt",
            "createdBy",
            "updatedAt",
            "updatedBy",
            "sourceLinks",
            "changeSummary",
            "notes",
        ]:
            with self.subTest(field=field_name):
                self.assertTrue(
                    schema["properties"][field_name]["$ref"].startswith(
                        "https://eos.local/schemas/common/metadata.schema.json#/properties/"
                    )
                )

    def test_material_reuses_property_record_classification_and_source_link(self) -> None:
        schema = self.validator.registry.by_id[MATERIAL_SCHEMA]
        self.assertEqual(
            schema["properties"]["properties"]["items"]["$ref"],
            PROPERTY_RECORD_SCHEMA,
        )
        self.assertEqual(
            schema["properties"]["classifications"]["items"]["$ref"],
            CLASSIFICATION_SCHEMA,
        )
        record = load_json(VALID_ENTITY_FIXTURES / "material-populated-source-links-valid.json")
        self.assertValid(record, MATERIAL_SCHEMA)

    def test_material_minimum_keeps_knowledge_fields_optional(self) -> None:
        record = load_json(VALID_ENTITY_FIXTURES / "material-minimal-draft-valid.json")
        for field_name in ["properties", "classifications", "description", "notes"]:
            with self.subTest(field=field_name):
                self.assertNotIn(field_name, record)
        self.assertValid(record, MATERIAL_SCHEMA)

    def test_material_preserves_duplicate_and_conflicting_claims(self) -> None:
        for name in [
            "material-same-property-multiple-valid.json",
            "material-conflicting-claims-valid.json",
        ]:
            with self.subTest(name=name):
                record = load_json(VALID_ENTITY_FIXTURES / name)
                self.assertEqual(record["properties"][0]["propertyId"], record["properties"][1]["propertyId"])
                self.assertValid(record, MATERIAL_SCHEMA)

    def test_material_source_lifecycle_rule_is_composed(self) -> None:
        draft = load_json(VALID_ENTITY_FIXTURES / "material-minimal-draft-valid.json")
        self.assertValid(draft, MATERIAL_SCHEMA)
        for status in ["Review", "Approved"]:
            with self.subTest(status=status):
                record = {**draft, "status": status}
                direct = self.validator.validate(record, MATERIAL_SCHEMA)
                self.assertIn(
                    ("application_validation.source_links_required", "$.sourceLinks"),
                    {(error.errorCode, error.path) for error in direct.errors},
                )
                indexed = self.validator.validate({"materials": [record]}, INDEX_SCHEMA)
                self.assertIn(
                    ("application_validation.source_links_required", "$.materials[0].sourceLinks"),
                    {(error.errorCode, error.path) for error in indexed.errors},
                )

    def test_material_replacement_links_are_structural_mat_references(self) -> None:
        for name in ["material-replaces-valid.json", "material-replaced-by-valid.json"]:
            with self.subTest(name=name):
                self.assertValid(load_json(VALID_ENTITY_FIXTURES / name), MATERIAL_SCHEMA)
        for name, path in [
            ("material-invalid-replaces-prefix-invalid.json", "$.replaces"),
            ("material-invalid-replaced-by-prefix-invalid.json", "$.replacedBy"),
        ]:
            with self.subTest(name=name):
                result = self.validator.validate(load_json(INVALID_ENTITY_FIXTURES / name), MATERIAL_SCHEMA)
                self.assertIn(
                    ("schema_validation.pattern", path),
                    {(error.errorCode, error.path) for error in result.errors},
                )

    def test_material_rejects_deferred_and_foreign_root_fields(self) -> None:
        names = [
            "material-verification-status-invalid.json",
            "material-designation-invalid.json",
            "material-designations-invalid.json",
            "material-material-condition-invalid.json",
            "material-delivery-condition-invalid.json",
            "material-heat-treatment-invalid.json",
            "material-chemical-composition-invalid.json",
            "material-norm-reference-ids-invalid.json",
            "material-supplier-id-invalid.json",
            "material-stock-forms-invalid.json",
            "material-observation-ids-invalid.json",
            "material-observations-invalid.json",
            "material-family-invalid.json",
            "material-type-invalid.json",
            "material-machine-ids-invalid.json",
            "material-cutting-tool-ids-invalid.json",
            "material-compatible-processes-invalid.json",
        ]
        for name in names:
            with self.subTest(name=name):
                result = self.validator.validate(load_json(INVALID_ENTITY_FIXTURES / name), MATERIAL_SCHEMA)
                self.assertIn("schema_validation.additionalProperties", [error.errorCode for error in result.errors])

    def test_material_rejects_root_conditions_but_allows_nested_condition(self) -> None:
        record = load_json(VALID_ENTITY_FIXTURES / "material-minimal-draft-valid.json")
        for field_name in ["condition", "conditions", "materialCondition", "deliveryCondition", "heatTreatment"]:
            with self.subTest(field=field_name):
                result = self.validator.validate({**record, field_name: []}, MATERIAL_SCHEMA)
                self.assertIn(
                    ("schema_validation.additionalProperties", f"$.{field_name}"),
                    {(error.errorCode, error.path) for error in result.errors},
                )
        nested = {
            **record,
            "properties": [{
                "propertyId": "PRP-980003",
                "valueType": "quantity",
                "quantity": {"value": 1, "unitId": "UNT-980001"},
                "conditions": [{
                    "conditionTypeId": "CND-980001",
                    "evaluationMode": "contextual",
                    "quantity": {"value": 1, "unitId": "UNT-980001"},
                }],
                "verificationStatus": "Draft",
                "sourceLinks": [],
            }],
        }
        self.assertValid(nested, MATERIAL_SCHEMA)

    def test_schema_index_resolves_material(self) -> None:
        schema = self.validator.registry.by_id[INDEX_SCHEMA]
        self.assertEqual(schema["$defs"]["material"]["$ref"], MATERIAL_SCHEMA)
        record = load_json(VALID_ENTITY_FIXTURES / "material-minimal-draft-valid.json")
        self.assertValid({"materials": [record]}, INDEX_SCHEMA)


if __name__ == "__main__":
    unittest.main()
