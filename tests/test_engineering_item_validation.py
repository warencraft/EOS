"""CDR-0026: stable identity owns assignments, not release-specific claims."""

import unittest

from scripts.validation import ValidationContext
from tests.owned_claim_checks import OwnedClassificationChecks, diagnostics
from tests.test_catalog_validation import build_registry, classification
from tests.validation_support import BASE, entity_fixture


class EngineeringItemValidationTests(OwnedClassificationChecks, unittest.TestCase):
    family = "engineering-item"
    uri = BASE + "entities/engineering-item.schema.json"

    def test_second_assignment_resolves_or_reports_only_its_missing_cls(self):
        item = entity_fixture(self.family, "populated-source-links")
        ctx = ValidationContext(build_registry())
        children = [classification(), classification()]
        item["classifications"] = children
        self.assertTrue(self.validator.validate_with_context(item, self.uri, ctx).ok)
        children[1] = classification("CLS-999999")
        result = self.validator.validate_with_context(item, self.uri, ctx)
        self.assertEqual(diagnostics(result), [
            ("reference_integrity.reference_not_found", "$.classifications[1].classificationId",
             item["id"], "CLS-999999", "error")])

    def test_assignment_evidence_does_not_substitute_for_identity_evidence(self):
        item = entity_fixture(self.family, "populated-source-links")
        item["classifications"][0]["sourceLinks"] = item["sourceLinks"]
        item["sourceLinks"] = []
        self.assertEqual(diagnostics(self.validator.validate(item, self.uri)), [
            ("application_validation.source_links_required", "$.sourceLinks", item["id"], None, "error")])
