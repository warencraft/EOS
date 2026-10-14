from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator

from scripts.validation import (
    CatalogKind,
    CatalogLifecyclePolicy,
    CatalogRecord,
    CatalogRegistry,
    EosValidator,
    ValidationContext,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://eos.local/schemas/"
SUPPLIER = BASE + "entities/supplier.schema.json"
INDEX = BASE + "index.schema.json"
VALID = ROOT / "tests/fixtures/valid/entities"
INVALID = ROOT / "tests/fixtures/invalid/entities"


def fixture(name: str = "minimal-draft") -> dict:
    return json.loads((VALID / f"supplier-{name}-valid.json").read_text(encoding="utf-8"))


class SupplierValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = EosValidator()
        cls.schema = cls.validator.registry.by_id[SUPPLIER]
        data = json.loads(
            (ROOT / "tests/fixtures/catalog-context/fictional-catalog-context.json").read_text(encoding="utf-8")
        )
        cls.entries = data["classificationEntries"]
        cls.context = ValidationContext(CatalogRegistry(classification_entries=cls.entries))

    def assert_valid(self, record: dict) -> None:
        result = self.validator.validate(record, SUPPLIER)
        self.assertTrue(result.ok, [(e.category, e.path, e.message) for e in result.errors])

    def test_schema_definition_and_closed_shape(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        self.assertTrue(self.validator.validate_schema_definition(SUPPLIER).ok)
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(self.schema["type"], "object")
        self.assertIs(self.schema["additionalProperties"], False)

    def test_valid_fixtures(self) -> None:
        files = sorted(VALID.glob("supplier-*-valid.json"))
        self.assertEqual(len(files), 12)
        for file in files:
            with self.subTest(file=file.name):
                result = self.validator.validate_json_file(file, SUPPLIER)
                self.assertTrue(result.ok, result.errors)

    def test_invalid_fixtures(self) -> None:
        files = sorted(INVALID.glob("supplier-*-invalid.json"))
        self.assertEqual(len(files), 131)
        for file in files:
            with self.subTest(file=file.name):
                result = self.validator.validate_json_file(file, SUPPLIER)
                self.assertFalse(result.ok, file.name)
                self.assertTrue(any(e.category == "schema_validation" for e in result.errors))
                self.assertFalse(any(e.category == "schema_definition" for e in result.errors))

    def test_sup_reuses_exact_central_definition(self) -> None:
        ref = BASE + "common/identifiers.schema.json#/$defs/SUP"
        self.assertEqual(self.schema["properties"]["id"]["$ref"], ref)
        self.assertNotIn("pattern", self.schema["properties"]["id"])
        self.assertEqual(self.validator.registry.get(ref)["pattern"], "^SUP-[0-9]{4}$")
        for value in ("SUP-0001", "SUP-9001", "SUP-9999"):
            self.assert_valid({**fixture(), "id": value})

    def test_common_metadata_refs_and_required_fields(self) -> None:
        metadata = self.validator.registry.by_id[BASE + "common/metadata.schema.json"]
        self.assertEqual(set(self.schema["required"]), set(metadata["required"]) | {"name"})
        for field in (set(metadata["required"]) - {"id"}) | {"notes"}:
            with self.subTest(field=field):
                ref = BASE + "common/metadata.schema.json#/properties/" + field
                self.assertEqual(self.schema["properties"][field]["$ref"], ref)
                self.assertEqual(self.validator.registry.get(ref), metadata["properties"][field])
        self.assertEqual(set(self.schema["properties"]) - set(self.schema["required"]),
                         {"description", "classifications", "notes"})

    def test_minimum_needs_no_optional_or_deferred_fields(self) -> None:
        record = fixture()
        self.assertEqual(set(record), set(self.schema["required"]))
        for field in ("description", "notes", "classifications", "addresses", "contacts",
                      "externalIdentifiers", "qualificationStatus", "certifications",
                      "capabilities", "price", "leadTime"):
            self.assertNotIn(field, record)
        self.assert_valid(record)

    def test_name_is_label_without_uniqueness_or_normalization(self) -> None:
        record = fixture()
        before = copy.deepcopy(record)
        self.assert_valid(record)
        self.assert_valid({**record, "id": "SUP-9002"})
        self.assertEqual(record, before)
        self.assert_valid({**record, "name": "  Fiktívny názov  "})

    def test_description_and_common_notes_semantics(self) -> None:
        self.assert_valid(fixture("description"))
        self.assert_valid(fixture("notes"))
        self.assert_valid({**fixture(), "notes": ""})
        self.assertFalse(self.validator.validate({**fixture(), "description": ""}, SUPPLIER).ok)

    def test_source_links_reuses_source_link_contract(self) -> None:
        ref = self.schema["properties"]["sourceLinks"]["$ref"]
        self.assertEqual(self.validator.registry.get(ref)["items"]["$ref"], BASE + "common/source-link.schema.json")
        self.assert_valid(fixture("populated-source-links"))

    def test_source_links_required_with_exact_path(self) -> None:
        record = fixture()
        del record["sourceLinks"]
        result = self.validator.validate(record, SUPPLIER)
        self.assertIn(("schema_validation.required", "$.sourceLinks"),
                      [(e.errorCode, e.path) for e in result.errors])

    def test_review_approved_require_root_provenance(self) -> None:
        self.assert_valid(fixture())
        for status in ("Review", "Approved"):
            with self.subTest(status=status):
                result = self.validator.validate({**fixture(), "status": status}, SUPPLIER)
                self.assertEqual([(e.category, e.errorCode, e.path) for e in result.errors],
                                 [("application_validation", "application_validation.source_links_required", "$.sourceLinks")])
                self.assert_valid({**fixture("populated-source-links"), "status": status})

    def test_assignment_sources_do_not_replace_root_sources(self) -> None:
        record = fixture("multiple-classifications")
        record["status"] = "Approved"
        self.assertTrue(record["classifications"][1]["sourceLinks"])
        result = self.validator.validate(record, SUPPLIER)
        self.assertIn("$.sourceLinks", [e.path for e in result.errors])

    def test_lifecycle_uses_record_status_not_business_status(self) -> None:
        for status in ("Draft", "Review", "Approved", "Deprecated", "Archived"):
            self.assert_valid({**fixture("populated-source-links"), "status": status})
        for status in ("Qualified", "ActiveVendor", "Accepted"):
            self.assertFalse(self.validator.validate({**fixture(), "status": status}, SUPPLIER).ok)

    def test_multiple_classifications_and_assignment_ref(self) -> None:
        self.assertEqual(self.schema["properties"]["classifications"]["items"]["$ref"],
                         BASE + "knowledge-core/classification.schema.json")
        for name in ("empty-classifications", "one-classification", "multiple-classifications"):
            self.assert_valid(fixture(name))
        self.assertEqual(len(fixture("multiple-classifications")["classifications"]), 2)

    def test_every_deferred_fixture_fails_as_unknown_field(self) -> None:
        for file in sorted(INVALID.glob("supplier-deferred-*-invalid.json")):
            field = file.name.removeprefix("supplier-deferred-").removesuffix("-invalid.json")
            with self.subTest(field=field):
                record = json.loads(file.read_text(encoding="utf-8"))
                result = self.validator.validate(record, SUPPLIER)
                self.assertEqual([(e.errorCode, e.path) for e in result.errors],
                                 [("schema_validation.additionalProperties", f"$.{field}")])
                del record[field]
                self.assert_valid(record)

    def test_observation_accepts_sup_subject_without_ownership(self) -> None:
        files = sorted((ROOT / "tests/fixtures/valid/knowledge-core").glob("observation-*-valid.json"))
        self.assertTrue(files)
        record = json.loads(files[0].read_text(encoding="utf-8"))
        record["subjectId"] = "SUP-9001"
        self.assertTrue(self.validator.validate(record, BASE + "knowledge-core/observation.schema.json").ok)
        for field in ("observations", "observationIds", "properties"):
            self.assertNotIn(field, self.schema["properties"])

    def test_index_definition_resolves_without_entity_collection(self) -> None:
        index = self.validator.registry.by_id[INDEX]
        self.assertEqual(index["$defs"]["supplier"]["$ref"], SUPPLIER)
        self.assertNotIn("suppliers", index["properties"])
        validator = Draft202012Validator(
            {"$ref": INDEX + "#/$defs/supplier"},
            registry=self.validator.referencing_registry,
            format_checker=self.validator.format_checker,
        )
        self.assertFalse(list(validator.iter_errors(fixture())))
        self.assertTrue(list(validator.iter_errors({**fixture(), "id": "MAT-9001"})))

    def test_contract_only_needs_no_catalog_registry(self) -> None:
        for record in (fixture(), fixture("empty-classifications"), fixture("one-classification")):
            self.assert_valid(record)
        result = self.validator.validate_with_context(fixture(), SUPPLIER, ValidationContext(CatalogRegistry()))
        self.assertTrue(result.ok)

    def test_context_requires_explicit_context_consistently(self) -> None:
        result = self.validator.validate_with_context(fixture(), SUPPLIER, None)
        self.assertEqual([e.errorCode for e in result.errors], ["catalog_validation.context_required"])

    def test_context_valid_cls_and_multiple_assignments(self) -> None:
        record = fixture("one-classification")
        record["classifications"] *= 2
        before = copy.deepcopy(record)
        result = self.validator.validate_with_context(record, SUPPLIER, self.context)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(record, before)

    def test_context_missing_cls_keeps_nested_path_and_root_id(self) -> None:
        record = fixture("one-classification")
        record["classifications"].append({"classificationId": "CLS-999999"})
        result = self.validator.validate_with_context(record, SUPPLIER, self.context)
        self.assertEqual([(e.category, e.path, e.recordId, e.referencedId) for e in result.errors],
                         [("reference_integrity", "$.classifications[1].classificationId", "SUP-9001", "CLS-999999")])

    def test_context_cls_type_check_is_reused(self) -> None:
        wrong = CatalogRecord(CatalogKind.UNIT, {"id": "CLS-980001", "status": "Approved"})
        with patch.object(CatalogRegistry, "resolve", return_value=wrong):
            result = self.validator.validate_with_context(fixture("one-classification"), SUPPLIER, self.context)
        self.assertEqual([(e.errorCode, e.path) for e in result.errors],
                         [("reference_integrity.reference_type_mismatch", "$.classifications[0].classificationId")])

    def test_context_cls_lifecycle_default_and_authoring(self) -> None:
        for entry in self.entries:
            for policy in (CatalogLifecyclePolicy.DEFAULT, CatalogLifecyclePolicy.AUTHORING):
                with self.subTest(status=entry["status"], policy=policy):
                    record = {**fixture(), "classifications": [{"classificationId": entry["id"]}]}
                    result = self.validator.validate_with_context(record, SUPPLIER, ValidationContext(self.context.catalogs, policy))
                    self.assertEqual(result.ok, policy.allows(entry["status"]))
                    if not result.ok:
                        self.assertEqual([(e.category, e.path) for e in result.errors],
                                         [("catalog_validation", "$.classifications[0].classificationId")])
                    if entry["status"] == "Deprecated":
                        self.assertEqual([e.errorCode for e in result.warnings], ["catalog_validation.deprecated_reference"])

    def test_nested_schema_errors_preserve_exact_paths(self) -> None:
        record = fixture("one-classification")
        record["classifications"][0]["sourceLinks"] = [{"sourceReferenceId": "SUP-9001"}]
        result = self.validator.validate_with_context(record, SUPPLIER, self.context)
        self.assertIn(("schema_validation.pattern", "$.classifications[0].sourceLinks[0].sourceReferenceId"),
                      [(e.errorCode, e.path) for e in result.errors])
        self.assertNotIn("catalog_validation", result.executedLayers)


if __name__ == "__main__":
    unittest.main()
