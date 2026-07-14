from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.validation import EosValidator, MissingValidationDependencyError


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "valid"


SOURCE_SCHEMA = "https://eos.local/schemas/source-reference.schema.json"
NORM_SCHEMA = "https://eos.local/schemas/norm-reference.schema.json"
DOCUMENT_SCHEMA = "https://eos.local/schemas/document-record.schema.json"


def load_fixture(name: str) -> dict:
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
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


if __name__ == "__main__":
    unittest.main()
