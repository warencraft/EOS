"""Material-specific contextual diagnostics (ADR-0017, CDR-0016)."""
import unittest

from tests.owned_claim_checks import OwnedClaimChecks, diagnostics
from tests.test_catalog_validation import property_record
from tests.validation_support import BASE, entity_fixture


class MaterialMigrationTests(OwnedClaimChecks, unittest.TestCase):
    family = "material"
    uri = BASE + "entities/material.schema.json"
    claim_fixture = "one-property"

    def test_value_range_errors_keep_owning_record_id(self):
        material = entity_fixture("material")
        self.assertEqual(material["id"], "MAT-9001")
        for bounds, suffix, field in (
            ({"minValue": 2, "maxValue": 1}, "reversed_bounds", "minValue"),
            ({"maxValue": 1, "lowerInclusive": True}, "lower_inclusive_without_min", "lowerInclusive"),
            ({"minValue": 1, "upperInclusive": True}, "upper_inclusive_without_max", "upperInclusive"),
        ):
            value_range = {"unitId": "UNT-980001", **bounds}
            claim = {**property_record(value_type="valueRange"), "valueRange": value_range}
            record = {**material, "properties": [claim]}
            for schema, data, prefix, owner in (
                (self.uri, record, "$.properties[0].valueRange", "MAT-9001"),
                (BASE + "knowledge-core/value-range.schema.json", value_range, "$", None),
            ):
                with self.subTest(schema=schema, rule=suffix):
                    result = self.validator.validate(data, schema)
                    expected = [("application_validation.value_range_" + suffix, prefix + "." + field, owner, None, "error")]
                    if field in ("lowerInclusive", "upperInclusive"):
                        expected.append(("schema_validation.dependentRequired", prefix, owner, None, "error"))
                    self.assertCountEqual(diagnostics(result), expected)
