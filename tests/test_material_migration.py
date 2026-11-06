"""Material-specific contextual diagnostics (ADR-0017, CDR-0016)."""
import unittest

from scripts.validation import CatalogLifecyclePolicy, EosValidator, ValidationContext
from tests.test_catalog_validation import build_registry, classification, condition, load_catalog_data, property_record
from tests.validation_support import BASE, entity_fixture


URI = BASE + "entities/material.schema.json"


def diagnostics(result):
    return [(e.errorCode, e.path, e.recordId, e.referencedId, e.severity) for e in result.errors]


class MaterialMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = EosValidator()

    def test_unresolved_reference_has_no_dependent_diagnostics(self):
        ctx = ValidationContext(build_registry())
        for field, child, path, ref in (
            ("properties", property_record("PRP-999999"), "properties[0].propertyId", "PRP-999999"),
            ("properties", property_record(unit_id="UNT-999999"), "properties[0].quantity.unitId", "UNT-999999"),
            ("properties", property_record("PRP-980003", conditions=[condition("CND-999999")]),
             "properties[0].conditions[0].conditionTypeId", "CND-999999"),
            ("classifications", classification("CLS-999999"), "classifications[0].classificationId", "CLS-999999"),
        ):
            with self.subTest(ref=ref):
                record = {**entity_fixture("material"), field: [child]}
                result = self.validator.validate_with_context(record, URI, ctx)
                self.assertEqual(diagnostics(result), [
                    ("reference_integrity.reference_not_found", "$." + path, record["id"], ref, "error")])

    def test_root_and_claim_sources_remain_independent(self):
        record = entity_fixture("material", "one-property")
        links = entity_fixture("material", "populated-source-links")["sourceLinks"]
        for root, child in ((links, []), ([], links)):
            with self.subTest(root_populated=bool(root)):
                claim = {**record["properties"][0], "sourceLinks": child}
                data = {**record, "status": "Approved", "sourceLinks": root, "properties": [claim]}
                result = self.validator.validate(data, URI)
                expected = [] if root else [
                    ("application_validation.source_links_required", "$.sourceLinks", record["id"], None, "error")]
                self.assertEqual(diagnostics(result), expected)
                self.assertEqual(data["properties"][0]["sourceLinks"], child)

    def test_cls_lifecycle_matrix_on_material(self):
        for status in ("Draft", "Review", "Approved", "Deprecated", "Archived"):
            data = load_catalog_data()
            entry = data["classificationEntries"][0]
            entry["status"] = status
            for policy in (CatalogLifecyclePolicy.DEFAULT, CatalogLifecyclePolicy.AUTHORING):
                with self.subTest(status=status, policy=policy):
                    record = {**entity_fixture("material"), "classifications": [classification(entry["id"])]}
                    result = self.validator.validate_with_context(record, URI, ValidationContext(build_registry(data), policy))
                    allowed = status in {"Approved", "Deprecated"} or (
                        policy == CatalogLifecyclePolicy.AUTHORING and status in {"Draft", "Review"})
                    expected = []
                    if not allowed or status == "Deprecated":
                        code = "deprecated_reference" if allowed else "catalog_status_not_allowed"
                        expected = [("catalog_validation." + code, "$.classifications[0].classificationId",
                                     record["id"], entry["id"], "warning" if allowed else "error")]
                    self.assertEqual(diagnostics(result), expected)
                    self.assertEqual(result.ok, allowed)
