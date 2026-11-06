"""CDR-0021: a physical unit owns claims, not measurements or capabilities."""
import unittest

from scripts.validation import ValidationContext
from tests.owned_claim_checks import OwnedClaimChecks, diagnostics
from tests.test_catalog_validation import build_registry, condition, load_catalog_data, property_record
from tests.validation_support import BASE, FIXTURES, entity_fixture, load_json


class MachineValidationTests(OwnedClaimChecks, unittest.TestCase):
    family = "machine"
    uri = BASE + "entities/machine.schema.json"
    claim_fixture = "populated-source-links"

    def test_unit_claim_catalog_policy(self):
        ctx = ValidationContext(build_registry())
        unit = entity_fixture(self.family, self.claim_fixture)
        self.assertTrue(self.validator.validate_with_context(unit, self.uri, ctx).ok)
        for claim, code, path, ref in (
            (property_record(value_type="valueRange"), "value_type_not_allowed", "valueType", "PRP-980001"),
            (property_record(unit_id="UNT-980002"), "unit_not_allowed", "quantity.unitId", "UNT-980002"),
            (property_record(conditions=[condition()]), "condition_not_allowed", "conditions[0].conditionTypeId", "CND-980001"),
        ):
            with self.subTest(rule=code):
                record = {**unit, "properties": [unit["properties"][0], claim]}
                result = self.validator.validate_with_context(record, self.uri, ctx)
                self.assertEqual(diagnostics(result), [
                    ("catalog_validation." + code, "$.properties[1]." + path, unit["id"], ref, "error")])

    def test_property_lifecycle_is_checked_for_this_unit(self):
        data = load_catalog_data()
        unit = entity_fixture(self.family, self.claim_fixture)
        ref = unit["properties"][0]["propertyId"]
        next(e for e in data["propertyEntries"] if e["id"] == ref)["status"] = "Archived"
        result = self.validator.validate_with_context(unit, self.uri, ValidationContext(build_registry(data)))
        self.assertEqual(diagnostics(result), [
            ("catalog_validation.catalog_status_not_allowed", "$.properties[0].propertyId", unit["id"], ref, "error")])

    def test_nested_range_uses_application_rules(self):
        unit = entity_fixture(self.family)
        claim = property_record(value_type="valueRange")
        claim["valueRange"].update(minValue=2, maxValue=1)
        result = self.validator.validate({**unit, "properties": [claim]}, self.uri)
        self.assertEqual(diagnostics(result), [
            ("application_validation.value_range_reversed_bounds", "$.properties[0].valueRange.minValue", unit["id"], None, "error")])

    def test_identity_and_separate_observation(self):
        unit = entity_fixture(self.family)
        for record in ({**unit, "name": "Fiktívny názov"}, {**unit, "id": "MAC-9003"}):
            self.assertTrue(self.validator.validate(record, self.uri).ok)
        observation = load_json(FIXTURES / "valid/knowledge-core/observation-global-quantity-valid.json")
        self.assertTrue(self.validator.validate({**observation, "subjectId": unit["id"]},
                                               BASE + "knowledge-core/observation.schema.json").ok)
        index = self.validator.registry.by_id[BASE + "index.schema.json"]
        self.assertNotIn("machines", index["properties"])
